from collections.abc import Callable
from datetime import datetime, timezone
import hashlib
import re

from app.application.ports.player_identity import PlayerIdentity
from app.domain.repositories.auth_token_repository import AuthTokenRepository
from app.shared.errors import UnauthorizedError

_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DevPlayerIdentity(PlayerIdentity):
    """Identidad de jugador: resuelve tokens de sesión reales de AuthTokenRepository y, en desarrollo/pruebas,
    acepta también el id directo del jugador (p. ej. "Authorization: Bearer jugador-1").
    """

    def __init__(
        self,
        auth_tokens: AuthTokenRepository | None = None,
        clock: Callable[[], datetime] = _utcnow,
    ) -> None:
        self._auth_tokens = auth_tokens
        self._clock = clock

    def player_id_from_token(self, token: str) -> str:
        if self._auth_tokens is not None and token:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            stored = self._auth_tokens.find_by_digest(digest)
            if stored is not None and stored.purpose == "session" and not stored.is_expired(self._clock()):
                return stored.user_id
        if not _TOKEN_PATTERN.match(token):
            raise UnauthorizedError("Token de sesión inválido")
        return token
