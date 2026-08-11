from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas.catalogo import ProductoCreate, ProductoUpdate, ProductoResponse
from app.models.domain import CatalogoItem, AliadoComercial

router = APIRouter(prefix="/api/v1/catalogo", tags=["Gestión Catálogo (Aliados)"])

# ==========================================
# 1. CREATE: Crear un nuevo producto
# ==========================================
@router.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(producto: ProductoCreate, db: AsyncSession = Depends(get_db)):
    aliado = await db.get(AliadoComercial, producto.aliado_id)
    if not aliado:
        raise HTTPException(status_code=404, detail="El aliado comercial no existe.")
        
    nuevo_producto = CatalogoItem(**producto.model_dump())
    db.add(nuevo_producto)
    await db.commit()
    await db.refresh(nuevo_producto)
    return nuevo_producto

# ==========================================
# 2. READ (ALL): Obtener catálogo de un restaurante
# ==========================================
@router.get("/productos/aliado/{aliado_id}", response_model=List[ProductoResponse])
async def get_productos_by_aliado(aliado_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CatalogoItem).where(CatalogoItem.aliado_id == aliado_id).order_by(CatalogoItem.orden_display)
    )
    return result.scalars().all()

# ==========================================
# 3. READ (ONE): Obtener un producto por ID
# ==========================================
@router.get("/productos/{producto_id}", response_model=ProductoResponse)
async def get_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await db.get(CatalogoItem, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return producto

# ==========================================
# 4. UPDATE: Actualizar un producto
# ==========================================
@router.put("/productos/{producto_id}", response_model=ProductoResponse)
async def update_producto(producto_id: int, producto_actualizado: ProductoUpdate, db: AsyncSession = Depends(get_db)):
    producto = await db.get(CatalogoItem, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    
    # exclude_unset=True asegura que solo actualizamos los campos que realmente se enviaron en el JSON
    update_data = producto_actualizado.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(producto, key, value)
        
    await db.commit()
    await db.refresh(producto)
    return producto

# ==========================================
# 5. DELETE: Eliminar un producto
# ==========================================
@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await db.get(CatalogoItem, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
        
    await db.delete(producto)
    await db.commit()
    return None