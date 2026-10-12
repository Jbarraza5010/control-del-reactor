from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


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
        return next((u for u in self._users.values() if u.username == username), None)

    def save(self, entity: User) -> User:
        self._users[entity.id] = entity
        return entity
