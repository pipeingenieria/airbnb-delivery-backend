from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import get_db
from app.models.domain import PropiedadAirbnb, CatalogoItem

router = APIRouter(prefix="/api/v1/core/guest", tags=["Vista Huéspedes"])

@router.get("/property/{qr_token}")
async def get_guest_view_data(qr_token: str, db: AsyncSession = Depends(get_db)):
    # 1. Obtener la propiedad por su token
    res_prop = await db.execute(
        select(PropiedadAirbnb).where(PropiedadAirbnb.qr_access_token == qr_token)
    )
    propiedad = res_prop.scalar_one_or_none()
    
    if not propiedad or not propiedad.activo:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada o inactiva.")
        
    lat_prop = propiedad.latitud
    lng_prop = propiedad.longitud

    if not lat_prop or not lng_prop:
        raise HTTPException(status_code=404, detail="Propiedad sin coordenadas válidas.")

    # =================================================================================
    # 2. LA MAGIA ESPACIAL (Fórmula de Haversine en Raw SQL para máxima velocidad)
    # =================================================================================
    query_magica = text("""
        WITH ZonasValidas AS (
            -- Paso A: Encontrar todas las zonas activas que logran cubrir la propiedad
            SELECT id, nombre, latitud, longitud, radio
            FROM zonas_geograficas
            WHERE activo = true 
              AND (6371000 * acos(
                    cos(radians(latitud)) * cos(radians(:lat_prop)) * 
                    cos(radians(:lng_prop) - radians(longitud)) + 
                    sin(radians(latitud)) * sin(radians(:lat_prop))
                  )) <= radio
        )
        -- Paso B: Encontrar los aliados activos que estén dentro de esas zonas válidas
        SELECT DISTINCT a.id, a.nombre, a.logo_url, c.id as cat_id, c.nombre as cat_nombre, c.icono as cat_icono
        FROM aliados_comerciales a
        JOIN categorias_servicio c ON a.categoria_id = c.id
        JOIN ZonasValidas zv ON (
            6371000 * acos(
                cos(radians(zv.latitud)) * cos(radians(a.latitud)) * 
                cos(radians(a.longitud) - radians(zv.longitud)) + 
                sin(radians(zv.latitud)) * sin(radians(a.latitud))
            )
        ) <= zv.radio
        WHERE a.estado_operativo = 'Abierto';
    """)

    res_aliados = await db.execute(query_magica, {"lat_prop": lat_prop, "lng_prop": lng_prop})
    aliados_db = res_aliados.fetchall()

    if not aliados_db:
         raise HTTPException(status_code=404, detail="No hay aliados disponibles en la zona de cobertura.")

    categorias_dict = {}
    aliados_list = []
    
    for aliado in aliados_db:
        if aliado.cat_id not in categorias_dict:
            categorias_dict[aliado.cat_id] = {
                "id": aliado.cat_id, 
                "nombre": aliado.cat_nombre, 
                "icono": aliado.cat_icono
            }
            
        aliados_list.append({
            "id": aliado.id,
            "name": aliado.nombre,
            "category_id": aliado.cat_id,
            "rating": 4.8,
            "time": "30-45 min",
            "priceLevel": "$$",
            "tags": aliado.cat_nombre,
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
    res = await db.execute(
        select(CatalogoItem).where(CatalogoItem.aliado_id == aliado_id, CatalogoItem.disponible == True)
    )
    return res.scalars().all()
