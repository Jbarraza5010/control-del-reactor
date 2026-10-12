#!/bin/sh
set -e

echo "[entrypoint] Aplicando migraciones de la base de datos..."
npx prisma migrate deploy

echo "[entrypoint] Iniciando backend..."
exec node dist/server.js
