"""Puerto de persistencia para tokens de autenticación (verificación, recuperación y sesión)."""
from abc import ABC, abstractmethod

from app.domain.entities.auth_token import AuthToken, TokenPurpose


class AuthTokenRepository(ABC):
    @abstractmethod
    def save(self, token: AuthToken) -> AuthToken: ...

    @abstractmethod
    def find_by_digest(self, digest: str) -> AuthToken | None: ...

    @abstractmethod
    def delete_by_digest(self, digest: str) -> None: ...

    @abstractmethod
    def delete_by_user_and_purpose(self, user_id: str, purpose: TokenPurpose) -> None: ...

