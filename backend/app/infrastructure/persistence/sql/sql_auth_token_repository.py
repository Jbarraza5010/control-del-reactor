from datetime import timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.auth_token import AuthToken, TokenPurpose
from app.domain.repositories.auth_token_repository import AuthTokenRepository
from app.infrastructure.persistence.sql.models import AuthTokenModel


class SqlAuthTokenRepository(AuthTokenRepository):
    """Implementación de AuthTokenRepository sobre PostgreSQL/SQLite mediante SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, token: AuthToken) -> AuthToken:
        with self._session_factory.begin() as session:
            session.merge(
                AuthTokenModel(
                    digest=token.digest,
                    user_id=token.user_id,
                    purpose=token.purpose,
                    expires_at=token.expires_at,
                )
            )
        return token

    def find_by_digest(self, digest: str) -> AuthToken | None:
        with self._session_factory() as session:
            row = session.get(AuthTokenModel, digest)
            return _to_domain(row)

    def delete_by_digest(self, digest: str) -> None:
        with self._session_factory.begin() as session:
            session.execute(delete(AuthTokenModel).where(AuthTokenModel.digest == digest))

    def delete_by_user_and_purpose(self, user_id: str, purpose: TokenPurpose) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                delete(AuthTokenModel).where(
                    AuthTokenModel.user_id == user_id,
                    AuthTokenModel.purpose == purpose,
                )
            )


def _to_domain(row: AuthTokenModel | None) -> AuthToken | None:
    if row is None:
        return None
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return AuthToken(
        digest=row.digest,
        user_id=row.user_id,
        purpose=row.purpose,  # type: ignore[arg-type]
        expires_at=expires_at,
    )

