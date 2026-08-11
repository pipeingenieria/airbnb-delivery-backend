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
    PropiedadCreate, PropiedadUpdate, PropiedadResponse,
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

# ----------------------------------------------------
# PROPIEDADES (Apartamentos) - ¡Lógica QR incluida!
# ----------------------------------------------------
@router.post("/propiedades", response_model=PropiedadResponse, status_code=status.HTTP_201_CREATED)
async def create_propiedad(propiedad: PropiedadCreate, db: AsyncSession = Depends(get_db)):
    zona = await db.get(ZonaGeografica, propiedad.zona_id)
    if not zona:
        raise HTTPException(status_code=400, detail="La zona (edificio) no existe.")
        
    nueva = PropiedadAirbnb(**propiedad.model_dump())
    # Autogeneramos un token UUIDv4 criptográficamente seguro para el QR del apto
    nueva.qr_access_token = str(uuid.uuid4()) 
    
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.get("/propiedades", response_model=List[PropiedadResponse])
async def get_propiedades(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PropiedadAirbnb))
    return res.scalars().all()

# ----------------------------------------------------
# ALIADOS (Restaurantes)
# ----------------------------------------------------
@router.post("/aliados", response_model=AliadoResponse, status_code=status.HTTP_201_CREATED)
async def create_aliado(aliado: AliadoCreate, db: AsyncSession = Depends(get_db)):
    # Doble validación de integridad referencial
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


# ==========================================
# ACTUALIZAR Y ELIMINAR: CATEGORÍAS
# ==========================================
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

# ==========================================
# ACTUALIZAR Y ELIMINAR: ZONAS
# ==========================================
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

# ==========================================
# ACTUALIZAR Y ELIMINAR: PROPIEDADES
# ==========================================
@router.put("/propiedades/{propiedad_id}", response_model=PropiedadResponse)
async def update_propiedad(propiedad_id: int, propiedad_actualizada: PropiedadUpdate, db: AsyncSession = Depends(get_db)):
    propiedad = await db.get(PropiedadAirbnb, propiedad_id)
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada.")
    
    update_data = propiedad_actualizada.model_dump(exclude_unset=True)
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

# ==========================================
# ACTUALIZAR Y ELIMINAR: ALIADOS
# ==========================================
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