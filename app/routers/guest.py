from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.domain import PropiedadAirbnb, AliadoComercial, CategoriaServicio, CatalogoItem

router = APIRouter(prefix="/api/v1/core/guest", tags=["Vista Huéspedes"])

@router.get("/property/{qr_token}")
async def get_guest_view_data(qr_token: str, db: AsyncSession = Depends(get_db)):
    # 1. Buscar la propiedad y verificar que esté activa
    stmt = select(PropiedadAirbnb).options(selectinload(PropiedadAirbnb.zonas)).where(PropiedadAirbnb.qr_access_token == qr_token)
    res = await db.execute(stmt)
    propiedad = res.scalar_one_or_none()
    
    if not propiedad or not propiedad.activo:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada o inactiva.")
        
    zonas_ids = [z.id for z in propiedad.zonas]
    if not zonas_ids:
        raise HTTPException(status_code=404, detail="Propiedad sin cobertura logística.")

    # 2. FILTRADO ESTRICTO: Solo trae aliados cuya zona coincida Y su estado operativo sea exactamente "Abierto"
    res_aliados = await db.execute(
        select(AliadoComercial, CategoriaServicio)
        .join(CategoriaServicio, AliadoComercial.categoria_id == CategoriaServicio.id)
        .where(
            AliadoComercial.zona_id.in_(zonas_ids), 
            AliadoComercial.estado_operativo == "Abierto" # <-- Blindado aquí
        )
    )
    aliados_db = res_aliados.all()
    
    categorias_dict = {}
    aliados_list = []
    
    for aliado, cat in aliados_db:
        if cat.id not in categorias_dict:
            categorias_dict[cat.id] = {"id": cat.id, "nombre": cat.nombre, "icono": cat.icono}
            
        aliados_list.append({
            "id": aliado.id,
            "name": aliado.nombre,
            "category_id": cat.id,
            "rating": 4.8,
            "time": "30-45 min",
            "priceLevel": "$$",
            "tags": cat.nombre,
            "imageUrl": aliado.logo_url or "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&q=80"
        })
        
    return {
        "propiedad": {
            "nombre": propiedad.nombre,
            "anfitrion": propiedad.airbnb_nombre
        },
        "categorias": list(categorias_dict.values()),
        "aliados": aliados_list
    }

@router.get("/ally/{aliado_id}/catalog")
async def get_guest_catalog(aliado_id: int, db: AsyncSession = Depends(get_db)):
    # Traer solo productos disponibles
    res = await db.execute(select(CatalogoItem).where(CatalogoItem.aliado_id == aliado_id, CatalogoItem.disponible == True))
    return res.scalars().all()