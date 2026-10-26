"""Entidad de dominio para el perfil y estadísticas del jugador (US-008)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerProfile:
    user_id: str
    username: str
    matches_played: int = 0
    matches_won: int = 0
    total_points: int = 0

