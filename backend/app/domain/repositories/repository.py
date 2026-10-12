"""Contrato genérico de repositorio (patrón Repository)."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    @abstractmethod
    def find_by_id(self, entity_id: ID) -> T | None: ...

    @abstractmethod
    def save(self, entity: T) -> T: ...
