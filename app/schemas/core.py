from pydantic import BaseModel
from typing import Optional

# ==========================================
# CATEGORÍAS
# ==========================================
class CategoriaBase(BaseModel):
    nombre: str
    requiere_despacho: bool = True

class CategoriaCreate(CategoriaBase): pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
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

class PropiedadUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion_apto: Optional[str] = None
    activo: Optional[bool] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    zonas_ids: Optional[List[int]] = None

class PropiedadResponse(PropiedadBase):
    id: int
    qr_access_token: Optional[str] = None
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

class AliadoCreate(AliadoBase): pass

class AliadoUpdate(BaseModel):
    nombre: Optional[str] = None
    estado_operativo: Optional[str] = None

class AliadoResponse(AliadoBase):
    id: int
    class Config: from_attributes = True
    