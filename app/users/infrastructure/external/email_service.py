from typing import Optional
from app.users.application.ports.email_service import EmailService
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os

class SMTPEmailService(EmailService):
    """
    Implementación del servicio de email usando SMTP.
    Compatible con Gmail, SendGrid, Amazon SES, etc.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "Sistema de Catering"
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

        # Configurar Jinja2 para templates
        template_dir = os.path.join(
            os.path.dirname(__file__),
            "../../templates/emails"
        )
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_activation_email(
        self,
        to_email: str,
        user_name: str,
        activation_link: str,
        expires_in_hours: int = 48
    ) -> bool:
        """Envía email de activación de cuenta"""
        try:
            # Renderizar template
            template = self.jinja_env.get_template("activation_email.html")
            html_content = template.render(
                user_name=user_name,
                activation_link=activation_link,
                expires_in_hours=expires_in_hours
            )

            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = "Activa tu cuenta - Sistema de Catering"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Agregar contenido HTML
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Agregar versión texto plano
            text_content = f"""
            Hola {user_name},

            Tu cuenta ha sido creada en el Sistema de Catering.

            Para activar tu cuenta, haz clic en el siguiente enlace:
            {activation_link}

            Este enlace expirará en {expires_in_hours} horas.

            Si no solicitaste esta cuenta, puedes ignorar este mensaje.

            Saludos,
            Equipo de Sistema de Catering
            """
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

            # Enviar email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )

            return True

        except Exception as e:
            # Log error
            print(f"Error enviando email de activación: {e}")
            return False

    async def send_account_activated_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """Envía confirmación de cuenta activada"""
        try:
            # Renderizar template
            template = self.jinja_env.get_template("account_activated.html")
            html_content = template.render(user_name=user_name)

            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = "¡Cuenta activada exitosamente!"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Agregar contenido HTML
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Agregar versión texto plano
            text_content = f"""
            Hola {user_name},

            ¡Tu cuenta ha sido activada exitosamente!

            Ya puedes iniciar sesión en la aplicación móvil del Sistema de Catering
            con tu email y la contraseña que configuraste.

            Saludos,
            Equipo de Sistema de Catering
            """
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

            # Enviar email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )

            return True

        except Exception as e:
            # Log error
            print(f"Error enviando email de confirmación: {e}")
            return False