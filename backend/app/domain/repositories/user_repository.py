"""Puerto de persistencia de usuarios.

El dominio y los servicios dependen de ESTA interfaz; no saben si detrás hay
PostgreSQL (SQLAlchemy) o una lista en memoria (pruebas).
"""
from abc import abstractmethod

from app.domain.entities.user import User
from app.domain.repositories.repository import Repository


class UserRepository(Repository[User, str]):
    @abstractmethod
    def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def find_by_username(self, username: str) -> User | None: ...
