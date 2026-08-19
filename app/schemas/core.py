from pydantic import BaseModel
from typing import Optional

# ==========================================
# CATEGORÍAS
# ==========================================
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    activo: bool = True
    requiere_despacho: bool = True

class CategoriaCreate(CategoriaBase): pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    activo: Optional[bool] = None
    requiere_despacho: Optional[bool] = None

class CategoriaResponse(CategoriaBase):
    id: int
    class Config: from_attributes = True

# ==========================================
# ZONAS (Edificios/Nodos)
# ==========================================
class ZonaBase(BaseModel):
    nombre: str
    ciudad: str
    activo: bool = True
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    radio: Optional[int] = 1000

class ZonaCreate(ZonaBase): pass

class ZonaUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    activo: Optional[bool] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    radio: Optional[int] = None

class ZonaResponse(ZonaBase):
    id: int
    class Config: from_attributes = True

from pydantic import BaseModel
from typing import Optional, List

# ==========================================
# PROPIEDADES (Aptos individuales y Edificios)
# ==========================================
class PropiedadBase(BaseModel):
    nombre: str
    direccion_apto: Optional[str] = None
    activo: bool = True
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class PropiedadCreate(PropiedadBase): 
    zonas_ids: List[int] = []
    airbnb_nombre: str | None = None
    airbnb_telefono: str | None = None
    airbnb_correo: str | None = None
    imagen_url: Optional[str] = None

class PropiedadUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion_apto: Optional[str] = None
    activo: Optional[bool] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    zonas_ids: Optional[List[int]] = None
    airbnb_nombre: str | None = None
    airbnb_telefono: str | None = None
    airbnb_correo: str | None = None
    imagen_url: Optional[str] = None

class PropiedadResponse(PropiedadBase):
    id: int
    qr_access_token: Optional[str] = None
    airbnb_nombre: Optional[str] = None
    airbnb_telefono: Optional[str] = None
    airbnb_correo: Optional[str] = None
    imagen_url: Optional[str] = None  # <-- Añadir
    
    class Config: from_attributes = True

# NUEVO: DTO para la creación de edificios en lote desde el Frontend
class PropiedadBatchCreate(BaseModel):
    nombre_edificio: str
    latitud: float
    longitud: float
    apartamentos: List[str]  # Ej: ["101", "102", "201", "202"]
    zonas_ids: List[int] = []

# ==========================================
# ALIADOS (Restaurantes)
# ==========================================
class AliadoBase(BaseModel):
    nombre: str
    categoria_id: int
    zona_id: int
    estado_operativo: str = "Abierto"
    correo_contacto: Optional[str] = None
    nombre_contacto: Optional[str] = None # <-- AÑADIR ESTA LÍNEA
    telefono_contacto: Optional[str] = None
    logo_url: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class AliadoCreate(AliadoBase): pass

class AliadoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    zona_id: Optional[int] = None
    estado_operativo: Optional[str] = None
    correo_contacto: Optional[str] = None
    nombre_contacto: Optional[str] = None # <-- AÑADIR ESTA LÍNEA
    telefono_contacto: Optional[str] = None
    logo_url: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class AliadoResponse(AliadoBase):
    id: int
    qr_access_token: Optional[str] = None
    
    class Config: from_attributes = True


# ==========================================
# CATÁLOGO DE PRODUCTOS (Aliados)
# ==========================================
class CatalogoItemBase(BaseModel):
    seccion: str = "Menú Principal" # <-- NUEVO
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagen_url: Optional[str] = None
    disponible: bool = True
    orden_display: int = 0

class CatalogoItemCreate(CatalogoItemBase): pass

class CatalogoItemUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None
    orden_display: Optional[int] = None

class CatalogoItemResponse(CatalogoItemBase):
    id: int
    aliado_id: int
    class Config: from_attributes = True