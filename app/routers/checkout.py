import os
import mercadopago
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional

# Importamos la dependencia de BD y los modelos de tu diseño
from app.database import get_db
# Ajusta esta ruta según cómo se llame tu archivo de modelos (ej: app.models o app.domain)
from app.models.domain import PedidoTransaccion, DetallePedido, LiquidacionPago, CatalogoItem

# --- CONFIGURACIÓN TEMPORAL DE CONVERSIÓN ---
# Ponlo en True para convertir USD a Pesos Colombianos (COP) para pruebas en MP Colombia.
# Cuando pases a dólares reales, solo cambias esto a False o el multiplicador a 1.
USAR_CONVERSION_COP = True
TRM_USD_COP = 4200.0  # Puedes ajustar la tasa de cambio aquí fácilmente

router = APIRouter(prefix="/checkout", tags=["Checkout y Pagos"])

# Inicializamos el SDK de MercadoPago
mp_client = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

# --- ESQUEMAS PYDANTIC (Para recibir los datos del Frontend) ---
class ItemCarrito(BaseModel):
    item_id: int
    cantidad: int
    notas_personalizadas: Optional[str] = None

class CheckoutRequest(BaseModel):
    propiedad_id: int
    aliado_id: int
    huesped_nombre: str
    huesped_contacto: str
    items: List[ItemCarrito]
    return_url: str  # <--- NUEVO CAMPO OBLIGATORIO

# --- 1. ENDPOINT PARA CREAR LA ORDEN Y EL LINK DE PAGO ---
@router.post("/crear-preferencia")
async def crear_preferencia(req: CheckoutRequest, request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Buscar los productos en la BD para validar precios reales y no confiar en el front
    item_ids = [i.item_id for i in req.items]
    res = await db.execute(select(CatalogoItem).where(CatalogoItem.id.in_(item_ids)))
    productos_bd = {p.id: p for p in res.scalars().all()}
    
    if not productos_bd:
        raise HTTPException(status_code=400, detail="Productos no encontrados en el catálogo.")

    monto_total = 0.0
    items_para_mp = []
    
    # 2. Calcular el total y armar los items para MercadoPago
    for item_req in req.items:
        prod = productos_bd.get(item_req.item_id)
        if not prod:
            continue
            
        # Aplicamos la conversión temporal si está activa
        precio_unitario_base = float(prod.precio_base)
        if USAR_CONVERSION_COP:
            # Multiplicamos por la TRM y redondeamos a entero (exigencia de MP en COP)
            precio_final = int(round(precio_unitario_base * TRM_USD_COP))
        else:
            precio_final = int(round(precio_unitario_base))

        subtotal = precio_final * item_req.cantidad
        monto_total += subtotal
        
        items_para_mp.append({
            "title": prod.nombre,
            "quantity": item_req.cantidad,
            "unit_price": precio_final # ¡Entero y en pesos!
        })

    # 3. Crear el PedidoTransaccion en la BD
    nuevo_pedido = PedidoTransaccion(
        propiedad_id=req.propiedad_id,
        aliado_id=req.aliado_id,
        huesped_nombre=req.huesped_nombre,
        huesped_contacto=req.huesped_contacto,
        estado_operativo="Pendiente Pago",
        monto_total=monto_total
    )
    db.add(nuevo_pedido)
    await db.flush() # Flush para obtener el ID generado sin hacer commit aún
    
    # 4. Crear los Detalles y la Liquidación
    for item_req in req.items:
        prod = productos_bd.get(item_req.item_id)
        detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            item_id=prod.id,
            cantidad=item_req.cantidad,
            precio_unitario=prod.precio_base,
            notas_personalizadas=item_req.notas_personalizadas
        )
        db.add(detalle)
        
    liquidacion = LiquidacionPago(
        pedido_id=nuevo_pedido.id,
        monto_bruto=monto_total,
        comision_plataforma=monto_total * 0.10, # Ej: 10% de comisión
        monto_aliado=monto_total * 0.90,
        estado_pago="Pendiente"
    )
    db.add(liquidacion)
    await db.commit()

    # 5. Generar la Preferencia en MercadoPago
    try:
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
        base_url = f"{proto}://{host}"
        
        # --- SALVAVIDAS DE RED PARA LOCALHOST ---
        if "127.0.0.1" in base_url or "localhost" in base_url:
            base_url = "https://airbnb-delivery-api.fly.dev"
        # ----------------------------------------
        
        correo_comprador = req.huesped_contacto if "@" in req.huesped_contacto else "cliente@benestiq.com"
        
        preference_data = {
            "items": items_para_mp,
            "payer": {"email": correo_comprador},
            "back_urls": {
                "success": req.return_url, # <--- AHORA REGRESA EXACTAMENTE DE DONDE VINO
                "failure": req.return_url,
                "pending": req.return_url,
            },
            "auto_return": "approved",
            "external_reference": str(nuevo_pedido.id),
            "notification_url": f"{base_url}/api/v1/checkout/webhook"
        }
        
        print("💡 DATOS ENVIADOS A MP:", preference_data)
        
        pref = mp_client.preference().create(preference_data)
        
        print("💡 RESPUESTA DE MP:", pref)
        
        response_data = pref.get("response", {})
        init_point = response_data.get("init_point")

        preference_id = response_data.get("id")
        
        if not init_point:
            error_msg = str(pref.get("response", "Sin respuesta de MP"))
            print("❌ ERROR DE MERCADOPAGO:", error_msg)
            raise HTTPException(status_code=500, detail=f"Error MP: {error_msg}")
            
        # --- NUEVO: ACTUALIZAMOS LA LIQUIDACIÓN Y GUARDAMOS ---
        if preference_id:
            liquidacion.gateway_tx_id = f"PREF-{preference_id}"
            await db.commit()
            
        return {"ok": True, "init_point": init_point, "pedido_id": nuevo_pedido.id}
        
    except Exception as e:
        print("💥 ERROR CRÍTICO EN MP:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. WEBHOOK (Donde MercadoPago avisa si pagaron o no) ---
@router.post("/webhook")
async def mp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    
    topic = data.get("type") or data.get("topic")
    mp_id = data.get("data", {}).get("id") or data.get("id")
    
    if topic and "payment" in topic.lower() and mp_id:
        payment_resp = mp_client.payment().get(mp_id)
        payment = payment_resp.get("response", {})
        
        reference = payment.get("external_reference") # Este es nuestro pedido_id
        status = payment.get("status")
        
        if reference:
            # Buscamos el pedido en la BD
            res_ped = await db.execute(select(PedidoTransaccion).where(PedidoTransaccion.id == int(reference)))
            pedido = res_ped.scalar_one_or_none()
            
            res_liq = await db.execute(select(LiquidacionPago).where(LiquidacionPago.pedido_id == int(reference)))
            liquidacion = res_liq.scalar_one_or_none()
            
            if pedido and liquidacion:
                if status == "approved":
                    pedido.estado_operativo = "Aprobado - Por Preparar"
                    liquidacion.estado_pago = "Aprobado"
                elif status in ["rejected", "cancelled"]:
                    pedido.estado_operativo = "Rechazado"
                    liquidacion.estado_pago = "Rechazado"
                    
                liquidacion.gateway_tx_id = str(mp_id)
                liquidacion.metodo_pago = payment.get("payment_method_id", "MercadoPago")
                
                await db.commit()
                # Aquí podrías llamar a una función para notificar al Restaurante y al Huésped
                
    return {"ok": True}


# --- 3. VERIFICADOR DE ESTADO (Equivalente al de BotCompany) ---
@router.get("/status/{pedido_id}")
async def check_payment_status(pedido_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PedidoTransaccion).where(PedidoTransaccion.id == pedido_id))
    pedido = res.scalar_one_or_none()
    
    if not pedido:
        return {"ok": False, "error": "Pedido no encontrado"}
        
    return {
        "ok": True,
        "estado": pedido.estado_operativo # Retornará "Pendiente Pago", "Aprobado - Por Preparar" o "Rechazado"
    }