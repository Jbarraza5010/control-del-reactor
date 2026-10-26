"""Identidad Google y desafíos de un solo uso (US-006 opcional)."""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("google_challenges",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("cuentas_sociales",
        sa.Column("google_subject", sa.String(255), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("usuario_id", name="uq_cuenta_social_usuario"))


def downgrade():
    op.drop_table("cuentas_sociales")
    op.drop_table("google_challenges")
