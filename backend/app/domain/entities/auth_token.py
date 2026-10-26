"""Entidad de dominio para tokens de verificación, recuperación y sesión."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

TokenPurpose = Literal["verify", "reset", "session"]


@dataclass
class AuthToken:
    digest: str
    user_id: str
    purpose: TokenPurpose
    expires_at: datetime

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

