# ADR-005 — Docker multi-stage y Docker Compose con valores por defecto

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La DoD exige que la aplicación arranque con `docker compose up` desde un clon limpio, sin pasos manuales no documentados,
y la restricción RT-003 exige Docker para ejecutar y desplegar los componentes.

## Decisión
- **Dockerfile multi-stage** sobre `python:3.12-slim`: una etapa instala las dependencias en un entorno virtual y la imagen final solo copia el entorno y el código, con usuario no root y `HEALTHCHECK` en `/health`.
- **docker-compose.yml** con `db` (postgres:16-alpine con healthcheck `pg_isready`), `backend` (espera a `db` saludable) y `adminer` (visor de BD, solo desarrollo).
- Todas las variables tienen valor por defecto, así que no se necesita un archivo `.env` para arrancar. `.env.example` documenta lo que se puede cambiar.
- El contenedor ejecuta `alembic upgrade head` antes de iniciar uvicorn.
- Las dependencias están fijadas a versiones exactas en `requirements.txt` para que la imagen sea reproducible.
- El cliente Godot y el simulador del panel se ejecutan fuera de Docker.

## Alternativas consideradas
- **Base `python:3.12-alpine`:** imagen más pequeña, pero algunos paquetes con extensiones nativas (psycopg) dan problemas en musl; `slim` evita esos fallos.
- **Ejecutar las migraciones como servicio aparte:** más puro, pero complica el Compose para el tamaño del proyecto.

## Consecuencias
- (+) Un comando levanta backend, base de datos y visor, igual en las cuatro computadoras.
- (+) El volumen `pgdata` conserva los datos entre reinicios (`docker compose down -v` los borra).
- (−) Las contraseñas por defecto son solo para desarrollo; en producción deben venir de secretos del pipeline.
- (−) El script `docker-entrypoint.sh` debe conservar finales de línea LF (se fuerza con `.gitattributes`).
