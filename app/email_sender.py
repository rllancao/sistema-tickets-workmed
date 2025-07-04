# app/email_sender.py
import smtplib
from email.message import EmailMessage
import streamlit as st

def enviar_correo_finalizado(destinatario: str, titulo_ticket: str, id_ticket: str):
    """
    Envía un correo de notificación usando las credenciales guardadas en st.secrets.
    """
    # Obtiene las credenciales de forma segura desde Streamlit Secrets
    smtp_server = st.secrets["server"]
    port = st.secrets["port"]
    sender_email = st.secrets["email"]
    password = st.secrets["password"]

    # --- Lógica de tu script de correo ---
    msg = EmailMessage()
    msg['Subject'] = f"✅ Tu ticket ha sido finalizado: #{id_ticket[:8]}"
    msg['From'] = sender_email
    msg['To'] = destinatario
    
    # Cuerpo del correo en HTML
    msg.set_content(f"""
    <html>
    <body>
        <h2>Ticket Finalizado: {titulo_ticket}</h2>
        <p>Hola,</p>
        <p>Nos complace informarte que tu solicitud ha sido completada por nuestro equipo.</p>
        <p>Gracias por confiar en nosotros.</p>
    </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"Correo enviado exitosamente a {destinatario}")
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False