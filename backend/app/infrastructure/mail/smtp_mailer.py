import smtplib
from email.message import EmailMessage

from app.application.ports.mailer import MailMessage, Mailer


class SmtpMailer(Mailer):
    """Producción: envío real por SMTP."""

    def __init__(self, host: str, port: int, user: str | None, password: str | None, sender: str) -> None:
        self._host, self._port, self._user, self._password, self._sender = host, port, user, password, sender

    def send(self, message: MailMessage) -> None:
        email = EmailMessage()
        email["From"] = self._sender
        email["To"] = message.to
        email["Subject"] = message.subject
        email.set_content(message.text)

        if self._port == 465:
            server: smtplib.SMTP = smtplib.SMTP_SSL(self._host, self._port, timeout=10)
        else:
            server = smtplib.SMTP(self._host, self._port, timeout=10)
        with server:
            if self._port != 465:
                server.starttls()
            if self._user:
                server.login(self._user, self._password or "")
            server.send_message(email)
