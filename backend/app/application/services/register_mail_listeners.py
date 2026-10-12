"""Observador de los eventos de cuenta.

Cuando alguien se registra o pide recuperar su contraseña, se envía el correo
correspondiente. (Los enlaces reales los define Moisés.)
"""
from app.application.ports.mailer import MailMessage, Mailer
from app.shared.events import EventBus, PasswordResetRequested, UserRegistered


def register_mail_listeners(bus: EventBus, mailer: Mailer) -> None:
    def on_user_registered(event: UserRegistered) -> None:
        mailer.send(
            MailMessage(
                to=event.email,
                subject="Verifica tu correo - Control del Reactor",
                text=f"Tu código de verificación (válido 24 horas): {event.verification_token}",
            )
        )

    def on_password_reset(event: PasswordResetRequested) -> None:
        mailer.send(
            MailMessage(
                to=event.email,
                subject="Recupera tu contraseña - Control del Reactor",
                text=f"Tu código para restablecer la contraseña (válido 1 hora): {event.reset_token}",
            )
        )

    bus.subscribe(UserRegistered, on_user_registered)
    bus.subscribe(PasswordResetRequested, on_password_reset)
