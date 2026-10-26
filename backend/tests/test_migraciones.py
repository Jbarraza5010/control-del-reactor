"""Las migraciones de Alembic deben subir y bajar (DoD: scripts versionados y reversibles)."""
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_upgrade_y_downgrade(tmp_path, monkeypatch):
    db = tmp_path / "prueba.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    cfg = Config("alembic.ini")

    command.upgrade(cfg, "head")
    assert "usuarios" in inspect(create_engine(f"sqlite:///{db}")).get_table_names()

    command.downgrade(cfg, "base")
    assert "usuarios" not in inspect(create_engine(f"sqlite:///{db}")).get_table_names()
