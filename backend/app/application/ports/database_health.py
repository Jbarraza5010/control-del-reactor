"""Puerto: permite al health check preguntar "¿hay base de datos?" sin conocer SQLAlchemy."""
from abc import ABC, abstractmethod


class DatabaseHealth(ABC):
    @abstractmethod
    def ping(self) -> None:
        """Lanza una excepción si la base de datos no responde."""
