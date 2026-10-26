from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UsuarioModel(Base):
    """Tabla `usuarios`. La EXTIENDE Moisés (jugadores, partidas, récords) con migraciones de Alembic.

    La unicidad de username y email vive en la base de datos (RNF-007), no solo en el código.
    """

    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDIENTE_VERIFICACION")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    __table_args__ = (
        Index("uq_usuarios_email_lower", func.lower(email), unique=True),
        Index("uq_usuarios_username_lower", func.lower(username), unique=True),
    )


class AuthTokenModel(Base):
    __tablename__ = "auth_tokens"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    purpose: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        CheckConstraint("purpose IN ('verify', 'reset', 'session')", name="ck_token_purpose"),
        Index("ix_auth_tokens_user_purpose", "user_id", "purpose"),
        Index("ix_auth_tokens_expires", "expires_at"),
    )


class GoogleChallengeModel(Base):
    __tablename__ = "google_challenges"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CuentaSocialModel(Base):
    __tablename__ = "cuentas_sociales"
    google_subject: Mapped[str] = mapped_column(String(255), primary_key=True)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("usuario_id", name="uq_cuenta_social_usuario"),)


class PerfilJugadorModel(Base):
    __tablename__ = "perfiles_jugador"
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (CheckConstraint("nivel >= 1", name="ck_perfil_nivel"),)


class PartidaModel(Base):
    __tablename__ = "partidas"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    escenario: Mapped[str] = mapped_column(String(100), nullable=False)
    modo: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ESPERA")
    limite_segundos: Mapped[int] = mapped_column(Integer, nullable=False)
    puntuacion_objetivo: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("estado IN ('ESPERA','EN_CURSO','FINALIZADA','CANCELADA')", name="ck_partida_estado"),
        CheckConstraint("limite_segundos > 0 AND puntuacion_objetivo > 0", name="ck_partida_limites"),
        CheckConstraint("ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at)", name="ck_partida_fechas"),
        CheckConstraint("estado != 'FINALIZADA' OR ended_at IS NOT NULL", name="ck_partida_finalizada"),
        CheckConstraint("estado != 'EN_CURSO' OR started_at IS NOT NULL", name="ck_partida_iniciada"),
    )


class ParticipacionModel(Base):
    __tablename__ = "participaciones"
    partida_id: Mapped[str] = mapped_column(ForeignKey("partidas.id", ondelete="CASCADE"), primary_key=True)
    jugador_id: Mapped[str] = mapped_column(ForeignKey("perfiles_jugador.usuario_id", ondelete="RESTRICT"), primary_key=True)
    puntuacion: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    posicion: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (
        CheckConstraint("puntuacion >= 0", name="ck_participacion_puntuacion"),
        CheckConstraint("posicion IS NULL OR posicion >= 1", name="ck_participacion_posicion"),
        UniqueConstraint("partida_id", "posicion", name="uq_partida_posicion"),
        Index("ix_participaciones_jugador", "jugador_id"),
    )
