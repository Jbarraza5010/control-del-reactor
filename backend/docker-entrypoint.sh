#!/bin/sh
set -e

echo "[entrypoint] Aplicando migraciones de la base de datos..."
alembic upgrade head

echo "[entrypoint] Iniciando backend..."
exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
