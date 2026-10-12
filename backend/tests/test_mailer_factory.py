import pytest

from app.config import Settings
from app.infrastructure.mail.console_mailer import ConsoleMailer
from app.infrastructure.mail.mailer_factory import MailerFactory
from app.infrastructure.mail.smtp_mailer import SmtpMailer


def test_console_crea_console_mailer():
    assert isinstance(MailerFactory.create(Settings(mail_transport="console")), ConsoleMailer)


def test_smtp_con_host_crea_smtp_mailer():
    settings = Settings(mail_transport="smtp", smtp_host="smtp.test")
    assert isinstance(MailerFactory.create(settings), SmtpMailer)


def test_smtp_sin_host_es_error_de_configuracion():
    with pytest.raises(ValueError, match="SMTP_HOST"):
        MailerFactory.create(Settings(mail_transport="smtp"))
