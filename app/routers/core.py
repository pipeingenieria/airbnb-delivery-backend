import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.domain import ZonaGeografica, PropiedadAirbnb, AliadoComercial, CategoriaServicio
from app.schemas.core import (
    CategoriaCreate, CategoriaUpdate, CategoriaResponse,
    ZonaCreate, ZonaUpdate, ZonaResponse,
    PropiedadCreate, PropiedadUpdate, PropiedadResponse, PropiedadBatchCreate,
    AliadoCreate, AliadoUpdate, AliadoResponse
)

router = APIRouter(prefix="/api/v1/core", tags=["Gestión Core (Super Admin)"])

# ----------------------------------------------------
# CATEGORÍAS
# ----------------------------------------------------
@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(categoria: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    nueva = CategoriaServicio(**categoria.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.get("/categorias", response_model=List[CategoriaResponse])
async def get_categorias(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CategoriaServicio))
    return res.scalars().all()

@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(categoria_id: int, categoria_actualizada: CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    categoria = await db.get(CategoriaServicio, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    update_data = categoria_actualizada.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(categoria, key, value)
        
    await db.commit()
    await db.refresh(categoria)
    return categoria

@router.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    categoria = await db.get(CategoriaServicio, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    await db.delete(categoria)
    await db.commit()
    return None


# ----------------------------------------------------
# ZONAS (Nodos/Edificios)
# ----------------------------------------------------
@router.post("/zonas", response_model=ZonaResponse, status_code=status.HTTP_201_CREATED)
async def create_zona(zona: ZonaCreate, db: AsyncSession = Depends(get_db)):
    nueva = ZonaGeografica(**zona.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.get("/zonas", response_model=List[ZonaResponse])
async def get_zonas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ZonaGeografica))
    return res.scalars().all()

@router.put("/zonas/{zona_id}", response_model=ZonaResponse)
async def update_zona(zona_id: int, zona_actualizada: ZonaUpdate, db: AsyncSession = Depends(get_db)):
    zona = await db.get(ZonaGeografica, zona_id)
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada.")
    
    update_data = zona_actualizada.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(zona, key, value)
        
    await db.commit()
    await db.refresh(zona)
    return zona

@router.delete("/zonas/{zona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zona(zona_id: int, db: AsyncSession = Depends(get_db)):
    zona = await db.get(ZonaGeografica, zona_id)
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada.")
    await db.delete(zona)
    await db.commit()
    return None


# ----------------------------------------------------
# PROPIEDADES (Apartamentos y Edificios)
# ----------------------------------------------------
@router.post("/propiedades", response_model=PropiedadResponse, status_code=status.HTTP_201_CREATED)
async def create_propiedad(propiedad: PropiedadCreate, db: AsyncSession = Depends(get_db)):
    # 1. Crear instancia base
    nueva = PropiedadAirbnb(
        nombre=propiedad.nombre,
        direccion_apto=propiedad.direccion_apto,
        activo=propiedad.activo,
        latitud=propiedad.latitud,
        longitud=propiedad.longitud,
        qr_access_token=str(uuid.uuid4())
    )
    
    # 2. Buscar y enlazar zonas múltiples (Asíncrono)
    if propiedad.zonas_ids:
        res = await db.execute(select(ZonaGeografica).where(ZonaGeografica.id.in_(propiedad.zonas_ids)))
        zonas_db = res.scalars().all()
        if len(zonas_db) != len(propiedad.zonas_ids):
            raise HTTPException(status_code=400, detail="Una o más zonas especificadas no existen.")
        nueva.zonas = zonas_db
        
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.post("/propiedades/batch", status_code=status.HTTP_201_CREATED)
async def create_propiedades_batch(batch_in: PropiedadBatchCreate, db: AsyncSession = Depends(get_db)):
    if not batch_in.apartamentos:
        raise HTTPException(status_code=400, detail="Debe especificar al menos un apartamento.")

    zonas_db = []
    if batch_in.zonas_ids:
        res = await db.execute(select(ZonaGeografica).where(ZonaGeografica.id.in_(batch_in.zonas_ids)))
        zonas_db = res.scalars().all()
        if len(zonas_db) != len(batch_in.zonas_ids):
            raise HTTPException(status_code=400, detail="Una o más zonas especificadas no existen.")

    propiedades_creadas = []
    for apto in batch_in.apartamentos:
        nueva_prop = PropiedadAirbnb(
            nombre=f"{batch_in.nombre_edificio} - Apto {apto}",
            direccion_apto=apto,
            latitud=batch_in.latitud,
            longitud=batch_in.longitud,
            activo=True,
            qr_access_token=str(uuid.uuid4())
        )
        nueva_prop.zonas = zonas_db
        db.add(nueva_prop)
        propiedades_creadas.append(nueva_prop)

    await db.commit()
    
    return {
        "mensaje": f"Se crearon {len(propiedades_creadas)} propiedades con éxito para el edificio {batch_in.nombre_edificio}.",
        "total_creados": len(propiedades_creadas)
    }

@router.get("/propiedades", response_model=List[PropiedadResponse])
async def get_propiedades(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PropiedadAirbnb))
    return res.scalars().all()

from sqlalchemy.orm import selectinload # Asegúrate de que esta importación esté (puedes dejarla aquí adentro si quieres, pero mejor arriba)

@router.put("/propiedades/{propiedad_id}", response_model=PropiedadResponse)
async def update_propiedad(propiedad_id: int, propiedad_actualizada: PropiedadUpdate, db: AsyncSession = Depends(get_db)):
    
    # SOLUCIÓN: Cargar la propiedad trayendo sus zonas pre-cargadas para evitar el MissingGreenlet
    stmt = select(PropiedadAirbnb).options(selectinload(PropiedadAirbnb.zonas)).where(PropiedadAirbnb.id == propiedad_id)
    res_prop = await db.execute(stmt)
    propiedad = res_prop.scalar_one_or_none()
    
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada.")
    
    update_data = propiedad_actualizada.model_dump(exclude_unset=True)
    
    # Manejar actualización de zonas_ids de forma independiente
    if "zonas_ids" in update_data:
        zonas_ids = update_data.pop("zonas_ids")
        if zonas_ids:
            res_zonas = await db.execute(select(ZonaGeografica).where(ZonaGeografica.id.in_(zonas_ids)))
            propiedad.zonas = list(res_zonas.scalars().all())
        else:
            propiedad.zonas = []

    for key, value in update_data.items():
        setattr(propiedad, key, value)
        
    await db.commit()
    await db.refresh(propiedad)
    return propiedad

@router.delete("/propiedades/{propiedad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_propiedad(propiedad_id: int, db: AsyncSession = Depends(get_db)):
    propiedad = await db.get(PropiedadAirbnb, propiedad_id)
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada.")
    await db.delete(propiedad)
    await db.commit()
    return None


# ----------------------------------------------------
# ALIADOS (Restaurantes)
# ----------------------------------------------------
@router.post("/aliados", response_model=AliadoResponse, status_code=status.HTTP_201_CREATED)
async def create_aliado(aliado: AliadoCreate, db: AsyncSession = Depends(get_db)):
    zona = await db.get(ZonaGeografica, aliado.zona_id)
    categoria = await db.get(CategoriaServicio, aliado.categoria_id)
    
    if not zona or not categoria:
        raise HTTPException(status_code=400, detail="La zona o la categoría no son válidas.")
        
    nuevo = AliadoComercial(**aliado.model_dump())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("/aliados", response_model=List[AliadoResponse])
async def get_aliados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(AliadoComercial))
    return res.scalars().all()

@router.put("/aliados/{aliado_id}", response_model=AliadoResponse)
async def update_aliado(aliado_id: int, aliado_actualizado: AliadoUpdate, db: AsyncSession = Depends(get_db)):
    aliado = await db.get(AliadoComercial, aliado_id)
    if not aliado:
        raise HTTPException(status_code=404, detail="Aliado no encontrado.")
    
    update_data = aliado_actualizado.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(aliado, key, value)
        
    await db.commit()
    await db.refresh(aliado)
    return aliado

@router.delete("/aliados/{aliado_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aliado(aliado_id: int, db: AsyncSession = Depends(get_db)):
    aliado = await db.get(AliadoComercial, aliado_id)
    if not aliado:
        raise HTTPException(status_code=404, detail="Aliado no encontrado.")
    await db.delete(aliado)
    await db.commit()
    return None