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

# ==========================================
# PROPIEDADES (Aptos individuales)
# ==========================================
class PropiedadBase(BaseModel):
    nombre: str
    direccion_apto: Optional[str] = None
    zona_id: int
    activo: bool = True

class PropiedadCreate(PropiedadBase): pass

class PropiedadUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion_apto: Optional[str] = None
    activo: Optional[bool] = None

class PropiedadResponse(PropiedadBase):
    id: int
    qr_access_token: Optional[str] = None
    class Config: from_attributes = True

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