from app.domain.entities.auth_token import AuthToken, TokenPurpose
from app.domain.repositories.auth_token_repository import AuthTokenRepository


class InMemoryAuthTokenRepository(AuthTokenRepository):
    """Implementación en memoria de AuthTokenRepository para pruebas."""

    def __init__(self) -> None:
        self._tokens: dict[str, AuthToken] = {}

    def save(self, token: AuthToken) -> AuthToken:
        self._tokens[token.digest] = token
        return token

    def find_by_digest(self, digest: str) -> AuthToken | None:
        return self._tokens.get(digest)

    def delete_by_digest(self, digest: str) -> None:
        self._tokens.pop(digest, None)

    def delete_by_user_and_purpose(self, user_id: str, purpose: TokenPurpose) -> None:
        to_delete = [
            digest
            for digest, tok in self._tokens.items()
            if tok.user_id == user_id and tok.purpose == purpose
        ]
        for digest in to_delete:
            del self._tokens[digest]

