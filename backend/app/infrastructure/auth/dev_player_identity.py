import re

from app.application.ports.player_identity import PlayerIdentity
from app.shared.errors import UnauthorizedError

_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class DevPlayerIdentity(PlayerIdentity):
    """SOLO DESARROLLO: el token ES el id del jugador (p. ej. "Authorization: Bearer jugador-1").

    Existe porque el login todavía no emite tokens. No valida nada contra la base de datos, así que
    cualquiera puede hacerse pasar por otro jugador. Reemplazar antes del despliegue (Sprint 5).
    """

    def player_id_from_token(self, token: str) -> str:
        if not _TOKEN_PATTERN.match(token):
            raise UnauthorizedError("Token de sesión inválido")
        return token
