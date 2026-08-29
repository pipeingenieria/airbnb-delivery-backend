from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.domain import AliadoComercial, CatalogoItem, CategoriaServicio, PedidoTransaccion, DetallePedido, PropiedadAirbnb
from app.schemas.core import CatalogoItemCreate, CatalogoItemUpdate, CatalogoItemResponse

router = APIRouter(prefix="/api/v1/core/partner", tags=["Portal Aliados"])

# Función de seguridad: Verifica el QR
async def get_aliado_by_token(token: str, db: AsyncSession):
    res = await db.execute(select(AliadoComercial).where(AliadoComercial.qr_access_token == token))
    aliado = res.scalar_one_or_none()
    if not aliado:
        raise HTTPException(status_code=403, detail="Acceso denegado o token inválido.")
    return aliado

@router.get("/{token}")
async def get_portal_data(token: str, db: AsyncSession = Depends(get_db)):
    aliado = await get_aliado_by_token(token, db)
    # Traemos el catálogo de este aliado
    res_cat = await db.execute(select(CatalogoItem).where(CatalogoItem.aliado_id == aliado.id))
    catalogo = res_cat.scalars().all()

    # 1. Buscamos el nombre de la categoría en la BD
    cat = await db.get(CategoriaServicio, aliado.categoria_id)
    categoria_nombre = cat.nombre if cat else "General"

    # 2. Traemos el catálogo
    res_cat = await db.execute(select(CatalogoItem).where(CatalogoItem.aliado_id == aliado.id))
    catalogo = res_cat.scalars().all()
    
    return {
        "aliado": {
            "id": aliado.id,
            "nombre": aliado.nombre,
            "estado_operativo": aliado.estado_operativo,
            "logo_url": aliado.logo_url,
            "categoria": categoria_nombre # <-- NUEVO: Le enviamos esto a Angular
        },
        "catalogo": catalogo
    }

@router.post("/{token}/catalogo", response_model=CatalogoItemResponse)
async def add_item(token: str, item: CatalogoItemCreate, db: AsyncSession = Depends(get_db)):
    aliado = await get_aliado_by_token(token, db)
    nuevo = CatalogoItem(**item.model_dump(), aliado_id=aliado.id)
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.put("/{token}/catalogo/{item_id}", response_model=CatalogoItemResponse)
async def update_item(token: str, item_id: int, item: CatalogoItemUpdate, db: AsyncSession = Depends(get_db)):
    aliado = await get_aliado_by_token(token, db)
    res = await db.execute(select(CatalogoItem).where(CatalogoItem.id == item_id, CatalogoItem.aliado_id == aliado.id))
    db_item = res.scalar_one_or_none()
    if not db_item: 
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
        
    for k, v in item.model_dump(exclude_unset=True).items():
        setattr(db_item, k, v)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.delete("/{token}/catalogo/{item_id}")
async def delete_item(token: str, item_id: int, db: AsyncSession = Depends(get_db)):
    aliado = await get_aliado_by_token(token, db)
    res = await db.execute(select(CatalogoItem).where(CatalogoItem.id == item_id, CatalogoItem.aliado_id == aliado.id))
    db_item = res.scalar_one_or_none()
    if not db_item: 
        raise HTTPException(status_code=404)
    await db.delete(db_item)
    await db.commit()
    return {"message": "Eliminado"}


@router.get("/live-orders/{token}")
async def get_live_orders(token: str, db: AsyncSession = Depends(get_db)):
    # 1. Validar al aliado usando su token de acceso
    res_aliado = await db.execute(select(AliadoComercial).where(AliadoComercial.qr_access_token == token)) # O el campo de token que uses
    aliado = res_aliado.scalar_one_or_none()
    
    if not aliado:
        raise HTTPException(status_code=404, detail="Acceso denegado")
        
    # 2. Buscar pedidos pagados e incluir Propiedad y Productos anidados
    query = (
        select(PedidoTransaccion)
        .options(
            # Trae la info del Airbnb (dirección, nombre)
            selectinload(PedidoTransaccion.propiedad), 
            
            # Trae los items, y de cada 'DetallePedido', trae la info del 'CatalogoItem'[cite: 16]
            selectinload(PedidoTransaccion.detalles).selectinload(DetallePedido.item) 
        )
        .where(
            PedidoTransaccion.aliado_id == aliado.id,
            PedidoTransaccion.estado_operativo.in_(["Aprobado - Por Preparar", "En Camino"])
        )
        .order_by(PedidoTransaccion.creado_en.asc())
    )
    
    res_pedidos = await db.execute(query)
    pedidos = res_pedidos.scalars().all()
    
    return {"ok": True, "pedidos": pedidos}

from app.models.domain import LiquidacionPago # Asegúrate de importarlo arriba

@router.get("/history-orders/{token}")
async def get_history_orders(token: str, db: AsyncSession = Depends(get_db)):
    aliado = await get_aliado_by_token(token, db)
    
    # Consulta robusta con todas las relaciones cargadas
    query = (
        select(PedidoTransaccion)
        .options(
            selectinload(PedidoTransaccion.propiedad),
            selectinload(PedidoTransaccion.detalles).selectinload(DetallePedido.item),
            selectinload(PedidoTransaccion.liquidacion) # Trae el gateway_tx_id de MercadoPago
        )
        .where(PedidoTransaccion.aliado_id == aliado.id)
        .order_by(PedidoTransaccion.creado_en.desc())
    )
    
    res_pedidos = await db.execute(query)
    pedidos = res_pedidos.scalars().all()
    
    return {"ok": True, "pedidos": pedidos}


# Esquema para recibir el nuevo estado
class UpdateOrderStatus(BaseModel):
    estado: str

# El endpoint que te faltaba
@router.patch("/order/{pedido_id}/status")
async def update_order_status(pedido_id: int, payload: UpdateOrderStatus, db: AsyncSession = Depends(get_db)):
    # Buscamos el pedido en la base de datos
    res = await db.execute(select(PedidoTransaccion).where(PedidoTransaccion.id == pedido_id))
    pedido = res.scalar_one_or_none()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    # Actualizamos el estado operativo (ej. "En Camino" o "Entregado")
    pedido.estado_operativo = payload.estado
    
    # Guardamos los cambios
    await db.commit()
    
    return {"ok": True, "mensaje": f"Pedido {pedido_id} actualizado a {payload.estado}"}