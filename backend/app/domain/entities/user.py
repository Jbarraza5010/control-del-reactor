"""Entidad de dominio "Usuario" (ERS sección 6). Python puro: no depende de FastAPI ni de SQLAlchemy."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

UserStatus = Literal["PENDIENTE_VERIFICACION", "ACTIVA"]


@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    status: UserStatus
    created_at: datetime
