# core/email.py - Migración a Resend API

import resend
from core.settings import settings

# Configurar API key de Resend
resend.api_key = settings.RESEND_API_KEY

def enviar_correo(destino: str, token: str):
    """Envía correo de recuperación de contraseña usando Resend API."""
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    try:
        result = resend.Emails.send({
            "from": "onboarding@resend.dev",  # Cambiar en producción a tu dominio verificado
            "to": [destino],
            "subject": "Recupera tu acceso - Smart Trash",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; background-color: #f4f6f8; font-family: Arial, sans-serif; color: #333333;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f6f8; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="100%" max-width="600px" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                
                                <!-- Header -->
                                <tr>
                                    <td style="background-color: #0a4174; padding: 30px 20px; text-align: center;">
                                        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: normal;">Recupera tu acceso</h2>
                                    </td>
                                </tr>
                                
                                <!-- Contenido -->
                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <p style="font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">Hola,</p>
                                        <p style="font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                                            Hemos recibido una solicitud para restablecer la contraseña de tu cuenta. 
                                            Para continuar con el proceso, haz clic en el siguiente botón:
                                        </p>
                                        
                                        <!-- Botón -->
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td align="center" style="padding: 10px 0 30px 0;">
                                                    <a href="{link}" style="background-color: #4e8ea2; color: #ffffff; text-decoration: none; padding: 14px 30px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px;">Restablecer contraseña</a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <p style="font-size: 15px; line-height: 1.6; color: #555555; margin: 0 0 15px 0;">
                                            Este enlace es válido solo por <strong>15 minutos</strong>.
                                        </p>
                                        <p style="font-size: 15px; line-height: 1.6; color: #555555; margin: 0;">
                                            Si no realizaste esta solicitud, puedes ignorar de forma segura este mensaje; tu cuenta sigue protegida.
                                        </p>
                                        
                                        <!-- Divisor -->
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 35px 0 20px 0;">
                                            <tr>
                                                <td style="border-top: 1px solid #eeeeee;"></td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Fallback del link -->
                                        <p style="font-size: 13px; color: #888888; line-height: 1.5; margin: 0; word-break: break-all;">
                                            Si tienes problemas con el botón, copia y pega el siguiente enlace en tu navegador:<br>
                                            <a href="{link}" style="color: #0a4174; text-decoration: underline;">{link}</a>
                                        </p>
                                    </td>
                                </tr>
                                
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
        })
        print(f"✅ Correo enviado exitosamente a {destino}: {result}")
        return result
    except Exception as e:
        print(f"❌ Error enviando correo con Resend: {e}")
        raise

import asyncio

async def enviar_correo_async(destino: str, token: str):
    """Ejecuta el envío de correo en un thread separado para no bloquear el event loop."""
    print(f"🚀 Iniciando envío de correo asíncrono a: {destino}")
    await asyncio.to_thread(enviar_correo, destino, token)
    print("✅ Envío de correo completado")
