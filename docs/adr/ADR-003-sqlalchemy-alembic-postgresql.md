# ADR-003 — SQLAlchemy + Alembic sobre PostgreSQL con migraciones versionadas

**Estado:** Aceptada · **Responsables:** Ulfrán Rodríguez y Moisés Barboza

## Contexto
La restricción RT-004 exige base de datos persistente y la DoD exige scripts de migración versionados y reversibles.
RNF-007 exige que la base impida duplicados de correo y nombre de usuario incluso con solicitudes concurrentes.

## Decisión
PostgreSQL 16 como base de datos, SQLAlchemy 2 como ORM (driver psycopg 3) y Alembic para las migraciones (`alembic upgrade head` / `downgrade`).
Las restricciones de unicidad (`unique` en `email` y `username`) viven en la base, y el repositorio traduce el error de integridad a un `ConflictError`.
El acceso a datos queda detrás de interfaces de repositorio (ADR-004).

## Alternativas consideradas
- **SQL a mano con psycopg:** control total, pero se pierde el mapeo a objetos y hay que construir un sistema de migraciones propio.
- **Django ORM / Tortoise:** obligan a adoptar un framework completo o un modelo asíncrono que el equipo no necesita.

## Consecuencias
- (+) Migraciones en `backend/alembic/versions`, cada una con `upgrade` y `downgrade`; hay una prueba automática que sube y baja.
- (+) Las migraciones se aplican solas al arrancar el contenedor.
- (+) Los repositorios se prueban con SQLite en memoria con la misma lógica; el comportamiento específico de PostgreSQL se valida con `docker compose`.
- (−) Para consultas muy complejas (ranking del Sprint 4) puede ser necesario SQL explícito.
