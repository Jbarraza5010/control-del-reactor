"""Cuentas, perfiles, partidas y vista de récords; conserva la migración 0001.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # Si existen duplicados por mayúsculas, el índice falla sin borrar cuentas.
    op.create_index("uq_usuarios_email_lower", "usuarios", [sa.text("lower(email)")], unique=True)
    op.create_index("uq_usuarios_username_lower", "usuarios", [sa.text("lower(username)")], unique=True)
    op.create_table("auth_tokens",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(10), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("purpose IN ('verify', 'reset', 'session')", name="ck_token_purpose"))
    op.create_index("ix_auth_tokens_user_purpose", "auth_tokens", ["user_id", "purpose"])
    op.create_index("ix_auth_tokens_expires", "auth_tokens", ["expires_at"])
    op.create_table("perfiles_jugador",
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("nivel", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("nivel >= 1", name="ck_perfil_nivel"))
    op.execute("INSERT INTO perfiles_jugador (usuario_id) SELECT id FROM usuarios")
    op.create_table("partidas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("escenario", sa.String(100), nullable=False),
        sa.Column("modo", sa.String(50), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="ESPERA"),
        sa.Column("limite_segundos", sa.Integer(), nullable=False),
        sa.Column("puntuacion_objetivo", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("estado IN ('ESPERA','EN_CURSO','FINALIZADA','CANCELADA')", name="ck_partida_estado"),
        sa.CheckConstraint("limite_segundos > 0 AND puntuacion_objetivo > 0", name="ck_partida_limites"),
        sa.CheckConstraint("ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at)", name="ck_partida_fechas"),
        sa.CheckConstraint("estado != 'FINALIZADA' OR ended_at IS NOT NULL", name="ck_partida_finalizada"),
        sa.CheckConstraint("estado != 'EN_CURSO' OR started_at IS NOT NULL", name="ck_partida_iniciada"))
    op.create_table("participaciones",
        sa.Column("partida_id", sa.String(36), sa.ForeignKey("partidas.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("jugador_id", sa.String(36), sa.ForeignKey("perfiles_jugador.usuario_id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("puntuacion", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("posicion", sa.Integer()),
        sa.CheckConstraint("puntuacion >= 0", name="ck_participacion_puntuacion"),
        sa.CheckConstraint("posicion IS NULL OR posicion >= 1", name="ck_participacion_posicion"),
        sa.UniqueConstraint("partida_id", "posicion", name="uq_partida_posicion"))
    op.create_index("ix_participaciones_jugador", "participaciones", ["jugador_id"])
    # No duplica estadísticas mutables: solo agrega resultados de partidas terminadas.
    op.execute("""CREATE VIEW records_jugador AS
        SELECT p.jugador_id, m.modo, m.escenario,
               MAX(p.puntuacion) AS mejor_puntuacion,
               SUM(p.puntuacion) AS puntuacion_acumulada,
               COUNT(*) AS partidas_jugadas,
               SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) AS victorias
        FROM participaciones p JOIN partidas m ON m.id = p.partida_id
        WHERE m.estado = 'FINALIZADA'
        GROUP BY p.jugador_id, m.modo, m.escenario""")


def downgrade():
    op.execute("DROP VIEW records_jugador")
    op.drop_table("participaciones")
    op.drop_table("partidas")
    op.drop_table("perfiles_jugador")
    op.drop_table("auth_tokens")
    op.drop_index("uq_usuarios_username_lower", table_name="usuarios")
    op.drop_index("uq_usuarios_email_lower", table_name="usuarios")
