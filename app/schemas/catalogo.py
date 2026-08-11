from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagen_url: Optional[str] = None
    disponible: bool = True
    orden_display: int = 0
    aliado_id: int

class ProductoCreate(ProductoBase):
    pass

# DTO exclusivo para actualización (todos los campos opcionales)
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None
    orden_display: Optional[int] = None
    # No incluimos aliado_id porque un producto no debería cambiar de dueño

class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True