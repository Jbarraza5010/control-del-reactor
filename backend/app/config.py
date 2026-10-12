"""Capa de configuración: única puerta de entrada a las variables de entorno.

Si falta algo obligatorio o un valor es inválido, el proceso falla al arrancar (fail-fast).
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://reactor:reactor@localhost:5432/reactor"
    mail_transport: Literal["console", "smtp"] = "console"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_pass: str | None = None
    mail_from: str = "Control del Reactor <no-reply@reactor.local>"


@lru_cache
def get_settings() -> Settings:
    return Settings()
