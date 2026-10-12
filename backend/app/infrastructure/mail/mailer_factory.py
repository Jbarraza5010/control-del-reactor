from app.application.ports.mailer import Mailer
from app.config import Settings
from app.infrastructure.mail.console_mailer import ConsoleMailer
from app.infrastructure.mail.smtp_mailer import SmtpMailer


class MailerFactory:
    """Patrón Factory: decide QUÉ implementación de Mailer crear según la configuración.

    El resto del sistema solo ve la interfaz Mailer.
    """

    @staticmethod
    def create(settings: Settings) -> Mailer:
        if settings.mail_transport == "smtp":
            if not settings.smtp_host:
                raise ValueError("MAIL_TRANSPORT=smtp requiere SMTP_HOST")
            return SmtpMailer(
                settings.smtp_host,
                settings.smtp_port,
                settings.smtp_user,
                settings.smtp_pass,
                settings.mail_from,
            )
        return ConsoleMailer()
