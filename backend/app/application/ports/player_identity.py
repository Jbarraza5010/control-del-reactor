"""Puerto: "¿qué jugador es el dueño de este token de sesión?".

Las rutas de hardware dependen de ESTA interfaz, no del login. Mientras el login (US-005) no emita
tokens, el contenedor usa DevPlayerIdentity; cuando exista, se agrega la implementación real y se
cambia una línea en app/container.py, sin tocar nada de hardware.
"""
from abc import ABC, abstractmethod


class PlayerIdentity(ABC):
    @abstractmethod
    def player_id_from_token(self, token: str) -> str:
        """Devuelve el id del jugador. Lanza UnauthorizedError si el token no es válido."""
