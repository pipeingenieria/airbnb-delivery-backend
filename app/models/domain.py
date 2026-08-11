from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
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
    catalogo = relationship("CatalogoItem", back_populates="aliado")
    pedidos = relationship("PedidoTransaccion", back_populates="aliado")

class PropiedadAirbnb(Base):
    __tablename__ = "propiedades_airbnb"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion_apto = Column(String) # Nuevo: para identificar el apto específico
    zona_id = Column(Integer, ForeignKey("zonas_geograficas.id"))
    qr_access_token = Column(String, unique=True, index=True)
    activo = Column(Boolean, default=True)

    zona = relationship("ZonaGeografica", back_populates="propiedades")
    pedidos = relationship("PedidoTransaccion", back_populates="propiedad")

class CatalogoItem(Base):
    __tablename__ = "catalogo_items"

    id = Column(Integer, primary_key=True, index=True)
    aliado_id = Column(Integer, ForeignKey("aliados_comerciales.id"))
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio_base = Column(Float, nullable=False)
    imagen_url = Column(String)
    disponible = Column(Boolean, default=True)
    orden_display = Column(Integer, default=0)

    aliado = relationship("AliadoComercial", back_populates="catalogo")
    detalles_pedido = relationship("DetallePedido", back_populates="item")

class PedidoTransaccion(Base):
    __tablename__ = "pedidos_transaccion"

    id = Column(Integer, primary_key=True, index=True)
    propiedad_id = Column(Integer, ForeignKey("propiedades_airbnb.id"))
    aliado_id = Column(Integer, ForeignKey("aliados_comerciales.id"))
    huesped_nombre = Column(String)
    huesped_contacto = Column(String)
    estado_operativo = Column(String, default="Creado")
    monto_total = Column(Float, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    propiedad = relationship("PropiedadAirbnb", back_populates="pedidos")
    aliado = relationship("AliadoComercial", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
    liquidacion = relationship("LiquidacionPago", back_populates="pedido", uselist=False)

class DetallePedido(Base):
    __tablename__ = "detalles_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_transaccion.id"))
    item_id = Column(Integer, ForeignKey("catalogo_items.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    notas_personalizadas = Column(String)

    pedido = relationship("PedidoTransaccion", back_populates="detalles")
    item = relationship("CatalogoItem", back_populates="detalles_pedido")

class LiquidacionPago(Base):
    __tablename__ = "liquidaciones_pago"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos_transaccion.id"), unique=True)
    gateway_tx_id = Column(String, unique=True)
    metodo_pago = Column(String)
    monto_bruto = Column(Float, nullable=False)
    comision_plataforma = Column(Float, nullable=False)
    monto_aliado = Column(Float, nullable=False)
    estado_pago = Column(String, default="Pendiente")
    desembolsado_en = Column(DateTime(timezone=True))

    pedido = relationship("PedidoTransaccion", back_populates="liquidacion")