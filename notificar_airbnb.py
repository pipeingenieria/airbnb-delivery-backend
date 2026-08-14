import os
import smtplib
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def enviar_correo_acceso_airbnb(destinatario: str, nombre_anfitrion: str, nombre_apto: str, qr_token: str):
    """Envía un correo HTML elegante con el QR y la URL de acceso del apartamento."""
    if not SMTP_PASSWORD:
        print("⚠️ No hay contraseña SMTP configurada en el .env.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"🔑 Accesos y QR de Entrega - {nombre_apto}"
    msg["From"] = SMTP_FROM
    
    # Soporte para múltiples correos separados por coma o punto y coma
    lista_correos = [email.strip() for email in destinatario.replace(";", ",").split(",") if email.strip()]
    msg["To"] = ", ".join(lista_correos)

    # Construcción de la URL y petición del QR a la API
    url_acceso = f"https://airbnb-delivery-frontend.vercel.app/{qr_token}"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={url_acceso}&color=0f172a&bgcolor=ffffff"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <body style="margin:0; padding:20px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #1e293b; padding: 30px; border-radius: 16px; text-align: center; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <h1 style="color: #6366f1; margin-top: 0; font-size: 24px;">🏡 Loft El Poblado</h1>
            <h2 style="font-weight: 500;">Hola {nombre_anfitrion},</h2>
            <p style="color: #94a3b8; font-size: 16px; line-height: 1.5;">Tu propiedad <strong>{nombre_apto}</strong> ha sido activada en nuestro sistema de logística y entregas.</p>
            
            <div style="background-color: #0f172a; padding: 20px; border-radius: 12px; margin: 25px 0; border: 1px solid rgba(99, 102, 241, 0.2);">
                <p style="margin: 5px 0; color: #94a3b8; font-size: 14px;"><strong>Tu Enlace Directo:</strong></p>
                <a href="{url_acceso}" style="color: #6366f1; font-size: 16px; text-decoration: none; font-weight: bold; word-break: break-all;">{url_acceso}</a>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05);">
                    <p style="margin: 5px 0; color: #94a3b8; font-size: 14px;"><strong>Código QR de Accesos:</strong></p>
                    <p style="font-size: 13px; color: #f8fafc; line-height: 1.4;">Adjuntamos el código QR oficial en este correo. Puedes imprimirlo y colocarlo en el apartamento para que tus huéspedes escaneen y pidan directamente a la habitación.</p>
                </div>
            </div>
            
            <p style="font-size: 12px; color: #64748b; margin-top: 30px;">* Este es un correo automático. Si necesitas ayuda con el sistema, responde a este mensaje.</p>
        </div>
    </body>
    </html>
    """
    msg.add_alternative(html_content, subtype="html")

    # Intentar adjuntar el QR generado en vivo como archivo PNG
    try:
        qr_response = requests.get(qr_api_url)
        if qr_response.status_code == 200:
            msg.add_attachment(
                qr_response.content, 
                maintype="image", 
                subtype="png", 
                filename=f"QR_{nombre_apto.replace(' ', '_')}.png"
            )
    except Exception as e:
        print(f"⚠️ Alerta: No se pudo adjuntar el código QR de {nombre_apto}: {e}")

    # Envío a través del servidor SMTP (Gmail)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_FROM, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Correo de acceso y QR enviado con éxito a: {msg['To']}.")
    except Exception as e:
        print(f"❌ Error crítico al enviar correo: {e}")

# Ejemplo de uso:
# enviar_correo_acceso_airbnb("huesped@gmail.com", "María Gonzalez", "Edificio Torrenova - Apto 502", "token-alfanumerico-123")