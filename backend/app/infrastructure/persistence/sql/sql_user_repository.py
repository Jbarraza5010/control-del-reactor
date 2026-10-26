from datetime import timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.persistence.sql.models import PerfilJugadorModel, UsuarioModel
from app.shared.errors import ConflictError


class SqlUserRepository(UserRepository):
    """Implementación de UserRepository sobre PostgreSQL mediante SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def find_by_id(self, entity_id: str) -> User | None:
        with self._session_factory() as session:
            return _to_domain(session.get(UsuarioModel, entity_id))

    def find_by_email(self, email: str) -> User | None:
        with self._session_factory() as session:
            row = session.scalar(select(UsuarioModel).where(func.lower(UsuarioModel.email) == email.lower()))
            return _to_domain(row)

    def find_by_username(self, username: str) -> User | None:
        with self._session_factory() as session:
            row = session.scalar(select(UsuarioModel).where(func.lower(UsuarioModel.username) == username.lower()))
            return _to_domain(row)

    def save(self, entity: User) -> User:
        try:
            with self._session_factory.begin() as session:
                session.merge(
                    UsuarioModel(
                        id=entity.id,
                        username=entity.username,
                        email=entity.email.lower(),
                        password_hash=entity.password_hash,
                        status=entity.status,
                        created_at=entity.created_at,
                    )
                )
                session.flush()
                if session.get(PerfilJugadorModel, entity.id) is None:
                    session.add(PerfilJugadorModel(usuario_id=entity.id))
        except IntegrityError as exc:
            # La base garantiza la unicidad incluso ante solicitudes concurrentes (RNF-007).
            raise ConflictError("El nombre de usuario o el correo ya están registrados") from exc
        return entity


def _to_domain(row: UsuarioModel | None) -> User | None:
    if row is None:
        return None
    created_at = row.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return User(
        id=row.id,
        username=row.username,
        email=row.email,
        password_hash=row.password_hash,
        status=row.status,  # type: ignore[arg-type]
        created_at=created_at,
    )
