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

# =====================================================================
# CORREO 1: ANFITRIONES (PROPIEDADES)
# Tema: Índigo Tecnológico - Diseño Horizontal
# =====================================================================
def enviar_correo_acceso_airbnb(destinatario: str, nombre_anfitrion: str, nombre_apto: str, qr_token: str):
    """Envía un correo HTML horizontal y corporativo para Be-Nest IQ."""
    if not SMTP_PASSWORD:
        print("⚠️ No hay contraseña SMTP configurada en el .env.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"🔑 Ecosistema Activado: {nombre_apto} | Be-Nest IQ"
    msg["From"] = f"Be-Nest IQ <{SMTP_FROM}>"
    
    lista_correos = [email.strip() for email in destinatario.replace(";", ",").split(",") if email.strip()]
    msg["To"] = ", ".join(lista_correos)

    url_acceso = f"https://airbnb-delivery-frontend.vercel.app/{qr_token}"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={url_acceso}&color=0f172a&bgcolor=ffffff"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0B1120; color: #F3F4F6; -webkit-font-smoothing: antialiased;">
        
        <!-- TOP NAVBAR DE BORDE A BORDE -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; border-bottom: 1px solid #1F2937;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table width="100%" style="max-width: 700px; padding: 0 20px;" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="left" style="font-size: 16px; font-weight: 800; letter-spacing: 2px; color: #818CF8; text-transform: uppercase;">BE-NEST IQ</td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #10B981; letter-spacing: 1px; text-transform: uppercase;">● Ecosistema En Línea</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <!-- CUERPO PRINCIPAL -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0B1120;">
            <tr>
                <td align="center" style="padding: 50px 0;">
                    <table width="100%" style="max-width: 700px; padding: 0 20px;" cellpadding="0" cellspacing="0" border="0">
                        
                        <!-- TITULAR Y SALUDO -->
                        <tr>
                            <td align="left" style="padding-bottom: 35px;">
                                <h1 style="margin: 0 0 8px 0; font-size: 26px; font-weight: 600; color: #FFFFFF;">Hola, {nombre_anfitrion}</h1>
                                <p style="margin: 0; font-size: 16px; color: #9CA3AF; line-height: 1.5;">La propiedad <strong style="color: #FFFFFF;">{nombre_apto}</strong> ha sido integrada exitosamente a la red logística. Tus huéspedes ya tienen acceso directo a nuestro directorio de aliados comerciales.</p>
                            </td>
                        </tr>
                        
                        <!-- BLOQUE HORIZONTAL (GRID SPLIT) -->
                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; border: 1px solid #1F2937; border-radius: 8px;">
                                    <tr>
                                        <!-- Izquierda: Link y Data -->
                                        <td align="left" valign="middle" style="padding: 25px; border-right: 1px solid #1F2937; width: 65%;">
                                            <p style="margin: 0 0 6px 0; font-size: 11px; color: #818CF8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Enlace Exclusivo del Apto</p>
                                            <a href="{url_acceso}" style="margin: 0; font-size: 14px; color: #E5E7EB; text-decoration: none; word-break: break-all;">{url_acceso}</a>
                                        </td>
                                        <!-- Derecha: Botón de Acción -->
                                        <td align="center" valign="middle" style="padding: 25px; background-color: rgba(79, 70, 229, 0.05); width: 35%;">
                                            <a href="{url_acceso}" style="background-color: #4F46E5; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 13px; display: inline-block;">Ver Interfaz</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- NOTA DE ADJUNTO HORIZONTAL -->
                        <tr>
                            <td align="left">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td width="4" style="background-color: #818CF8;"></td>
                                        <td style="padding: 16px 20px; background-color: rgba(17, 24, 39, 0.6);">
                                            <p style="margin: 0; font-size: 14px; color: #9CA3AF; line-height: 1.5;"><strong style="color: #E5E7EB;">Código QR Adjunto:</strong> Hemos enviado el código QR oficial en los archivos de este correo. Imprímelo y ubícalo en el apartamento para facilitar el escaneo.</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
        
        <!-- FOOTER -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0B1120; border-top: 1px solid #1F2937;">
            <tr>
                <td align="center" style="padding: 30px 20px;">
                    <p style="margin: 0 0 5px 0; font-size: 12px; color: #4B5563; font-weight: 500;">© 2026 Be-Nest IQ. Tecnología en Logística y Hospitalidad.</p>
                    <p style="margin: 0; font-size: 11px; color: #374151;">Notificación automática del sistema.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    msg.add_alternative(html_content, subtype="html")

    try:
        qr_response = requests.get(qr_api_url)
        if qr_response.status_code == 200:
            msg.add_attachment(qr_response.content, maintype="image", subtype="png", filename=f"QR_{nombre_apto.replace(' ', '_')}.png")
    except Exception as e:
        print(f"⚠️ Alerta: No se pudo adjuntar el código QR: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_FROM, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ [Be-Nest IQ] Correo enviado a: {msg['To']}")
    except Exception as e:
        print(f"❌ Error crítico al enviar correo: {e}")


# =====================================================================
# CORREO 2: ALIADOS COMERCIALES
# Tema: Coral / Rose (Comercio / Acción) - Diseño Horizontal
# =====================================================================
def enviar_correo_acceso_aliado(destinatario: str, nombre_comercio: str, nombre_contacto: str, qr_token: str):
    """Envía un correo HTML horizontal y corporativo para los socios de Be-Nest IQ Partners."""
    if not SMTP_PASSWORD:
        print("⚠️ No hay contraseña SMTP configurada en el .env.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"🚀 Bienvenida a la Red Comercial: {nombre_comercio} | Be-Nest IQ"
    msg["From"] = f"Be-Nest IQ Partners <{SMTP_FROM}>"
    
    lista_correos = [email.strip() for email in destinatario.replace(";", ",").split(",") if email.strip()]
    msg["To"] = ", ".join(lista_correos)

    url_portal = f"https://airbnb-delivery-frontend.vercel.app/partner/{qr_token}"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={url_portal}&color=0f172a&bgcolor=ffffff"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0B1120; color: #F3F4F6; -webkit-font-smoothing: antialiased;">
        
        <!-- TOP NAVBAR DE BORDE A BORDE -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; border-bottom: 1px solid #1F2937;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table width="100%" style="max-width: 700px; padding: 0 20px;" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="left" style="font-size: 16px; font-weight: 800; letter-spacing: 2px; color: #FB7185; text-transform: uppercase;">BE-NEST IQ <span style="color: #64748B;">PARTNERS</span></td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #10B981; letter-spacing: 1px; text-transform: uppercase;">● Socio Verificado</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <!-- CUERPO PRINCIPAL -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0B1120;">
            <tr>
                <td align="center" style="padding: 50px 0;">
                    <table width="100%" style="max-width: 700px; padding: 0 20px;" cellpadding="0" cellspacing="0" border="0">
                        
                        <!-- TITULAR Y SALUDO -->
                        <tr>
                            <td align="left" style="padding-bottom: 35px;">
                                <h1 style="margin: 0 0 8px 0; font-size: 26px; font-weight: 600; color: #FFFFFF;">Hola, {nombre_contacto}</h1>
                                <p style="margin: 0; font-size: 16px; color: #9CA3AF; line-height: 1.5;">Es oficial. <strong style="color: #FFFFFF;">{nombre_comercio}</strong> forma parte de la red logística. A partir de hoy, tu comercio conectará directamente con los huéspedes en tu geocerca asignada.</p>
                            </td>
                        </tr>
                        
                        <!-- BLOQUE HORIZONTAL (GRID SPLIT) -->
                        <tr>
                            <td align="center" style="padding-bottom: 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #111827; border: 1px solid #1F2937; border-radius: 8px;">
                                    <tr>
                                        <!-- Izquierda: Link y Data -->
                                        <td align="left" valign="middle" style="padding: 25px; border-right: 1px solid #1F2937; width: 65%;">
                                            <p style="margin: 0 0 6px 0; font-size: 11px; color: #FB7185; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Portal de Administración</p>
                                            <p style="margin: 0; font-size: 13px; color: #9CA3AF;">Accede a tu panel para gestionar catálogo, horarios y procesar los pedidos de los huéspedes.</p>
                                        </td>
                                        <!-- Derecha: Botón de Acción -->
                                        <td align="center" valign="middle" style="padding: 25px; background-color: rgba(225, 29, 72, 0.05); width: 35%;">
                                            <a href="{url_portal}" style="background-color: #E11D48; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 13px; display: inline-block;">Ingresar al Panel</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- NOTA DE ADJUNTO HORIZONTAL -->
                        <tr>
                            <td align="left">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td width="4" style="background-color: #FB7185;"></td>
                                        <td style="padding: 16px 20px; background-color: rgba(17, 24, 39, 0.6);">
                                            <p style="margin: 0; font-size: 14px; color: #9CA3AF; line-height: 1.5;"><strong style="color: #E5E7EB;">Llave Maestra QR:</strong> Hemos adjuntado el QR de acceso a este correo. Escanéalo con tu celular para entrar de forma segura sin contraseñas.</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
        
        <!-- FOOTER -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0B1120; border-top: 1px solid #1F2937;">
            <tr>
                <td align="center" style="padding: 30px 20px;">
                    <p style="margin: 0 0 5px 0; font-size: 12px; color: #4B5563; font-weight: 500;">© 2026 Be-Nest IQ Partners. Creciendo juntos.</p>
                    <p style="margin: 0; font-size: 11px; color: #374151;">Mantén este correo a salvo. Es tu llave de acceso al sistema.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    msg.add_alternative(html_content, subtype="html")

    try:
        qr_response = requests.get(qr_api_url)
        if qr_response.status_code == 200:
            msg.add_attachment(qr_response.content, maintype="image", subtype="png", filename=f"QR_Portal_{nombre_comercio.replace(' ', '_')}.png")
    except Exception as e:
        print(f"⚠️ Alerta: No se pudo adjuntar el código QR: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_FROM, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ [Be-Nest IQ] Correo enviado a: {msg['To']}")
    except Exception as e:
        print(f"❌ Error crítico al enviar correo: {e}")