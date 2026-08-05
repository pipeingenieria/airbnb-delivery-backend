from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ZonaGeografica(Base):
    __tablename__ = "zonas_geograficas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    ciudad = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

    propiedades = relationship("PropiedadAirbnb", back_populates="zona")
    aliados = relationship("AliadoComercial", back_populates="zona")

class CategoriaServicio(Base):
    __tablename__ = "categorias_servicio"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False) 
    requiere_despacho = Column(Boolean, default=True)

    aliados = relationship("AliadoComercial", back_populates="categoria")

class AliadoComercial(Base):
    __tablename__ = "aliados_comerciales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_servicio.id"))
    zona_id = Column(Integer, ForeignKey("zonas_geograficas.id"))
    estado_operativo = Column(String, default="Abierto")

    categoria = relationship("CategoriaServicio", back_populates="aliados")
    zona = relationship("ZonaGeografica", back_populates="aliados")

class PropiedadAirbnb(Base):
    __tablename__ = "propiedades_airbnb"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas_geograficas.id"))
    qr_access_token = Column(String, unique=True, index=True)
    activo = Column(Boolean, default=True)

    zona = relationship("ZonaGeografica", back_populates="propiedades")
