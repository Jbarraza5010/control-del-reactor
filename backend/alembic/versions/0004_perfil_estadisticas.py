"""Resumen de perfil solicitado por el cliente; conserva tablas y referencias.

Revision ID: 0004
Revises: 0003
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE VIEW perfil_estadisticas AS
        SELECT u.id AS usuario_id,
               u.username AS nombre_usuario,
               CAST(COALESCE(SUM(r.partidas_jugadas), 0) AS BIGINT) AS partidas_jugadas,
               CAST(COALESCE(SUM(r.victorias), 0) AS BIGINT) AS partidas_ganadas,
               CAST(COALESCE(SUM(r.puntuacion_acumulada), 0) AS BIGINT) AS puntos_totales
        FROM usuarios u
        JOIN perfiles_jugador j ON j.usuario_id = u.id
        LEFT JOIN records_jugador r ON r.jugador_id = j.usuario_id
        GROUP BY u.id, u.username""")


def downgrade():
    op.execute("DROP VIEW perfil_estadisticas")
