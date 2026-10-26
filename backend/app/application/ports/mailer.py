"""Puerto de salida: la aplicación pide "enviar un correo" sin saber cómo se envía."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class MailMessage:
    to: str
    subject: str
    text: str


class Mailer(ABC):
    @abstractmethod
    def send(self, message: MailMessage) -> None: ...
