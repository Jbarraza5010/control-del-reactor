from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.shared.errors import ConflictError


class InMemoryUserRepository(UserRepository):
    """Implementación en memoria: permite probar la lógica sin base de datos."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def find_by_id(self, entity_id: str) -> User | None:
        return self._users.get(entity_id)

    def find_by_email(self, email: str) -> User | None:
        target = email.lower()
        return next((u for u in self._users.values() if u.email.lower() == target), None)

    def find_by_username(self, username: str) -> User | None:
        target = username.lower()
        return next((u for u in self._users.values() if u.username.lower() == target), None)

    def save(self, entity: User) -> User:
        for existing in self._users.values():
            if existing.id != entity.id and (
                existing.email.lower() == entity.email.lower()
                or existing.username.lower() == entity.username.lower()
            ):
                raise ConflictError("El nombre de usuario o el correo ya están registrados")
        self._users[entity.id] = entity
        return entity
