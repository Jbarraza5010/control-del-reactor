from sqlalchemy import Engine, text

from app.application.ports.database_health import DatabaseHealth


class SqlDatabaseHealth(DatabaseHealth):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def ping(self) -> None:
        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))
