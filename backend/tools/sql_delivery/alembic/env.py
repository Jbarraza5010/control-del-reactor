"""Entorno independiente para exportar/probar las migraciones de esta entrega.

El equipo conserva su backend/alembic/env.py. No sustituirlo por este archivo.
"""
import os
from alembic import context
from sqlalchemy import create_engine


if context.is_offline_mode():
    context.configure(url="postgresql+psycopg://", literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied = context.config.attributes.get("connection")
    if supplied is not None:
        context.configure(connection=supplied)
        with context.begin_transaction():
            context.run_migrations()
    else:
        # No hay servidor predeterminado ni contraseña incluida.
        engine = create_engine(os.environ["DATABASE_URL"])
        with engine.connect() as connection:
            context.configure(connection=connection)
            with context.begin_transaction():
                context.run_migrations()
        engine.dispose()
