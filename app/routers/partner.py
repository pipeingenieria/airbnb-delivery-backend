from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.domain import AliadoComercial, CatalogoItem
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
    
    return {
        "aliado": {
            "id": aliado.id,
            "nombre": aliado.nombre,
            "estado_operativo": aliado.estado_operativo,
            "logo_url": aliado.logo_url
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