from app.application.ports.mailer import MailMessage, Mailer
from app.shared.logger import get_logger

logger = get_logger()


class ConsoleMailer(Mailer):
    """Desarrollo: imprime el correo en el log (útil para copiar el código de verificación)."""

    def send(self, message: MailMessage) -> None:
        logger.info(
            "[correo simulado]",
            extra={"extra_data": {"to": message.to, "subject": message.subject, "text": message.text}},
        )
