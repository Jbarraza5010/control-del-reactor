# ADR-003 — Prisma ORM sobre PostgreSQL con migraciones versionadas

**Estado:** Aceptada · **Responsables:** Ulfrán Rodríguez y Moisés Barboza

## Contexto
La restricción RT-004 exige base de datos persistente y la DoD exige scripts de migración versionados y reversibles.
RNF-007 exige que la base impida duplicados de correo y usuario incluso con solicitudes concurrentes.

## Decisión
PostgreSQL 16 como base de datos y Prisma como ORM y herramienta de migraciones (`prisma migrate`).
Las restricciones de unicidad (`@unique` en `email` y `username`) viven en la base, no solo en el código.
El acceso a datos queda detrás de interfaces de repositorio (ADR-004).

## Alternativas consideradas
- **SQL a mano con `pg`:** control total, pero se pierde el tipado y hay que construir un sistema de migraciones propio.
- **TypeORM / Sequelize:** funcionan, pero Prisma ofrece mejor tipado y migraciones declarativas con menos configuración.

## Consecuencias
- (+) Esquema declarativo en `prisma/schema.prisma`, migraciones en `prisma/migrations`, cliente tipado.
- (+) Las migraciones se aplican solas al arrancar el contenedor (`prisma migrate deploy`).
- (−) El cliente Prisma debe generarse (`prisma generate`) antes de compilar; el Dockerfile y el CI lo hacen.
- (−) Para consultas muy complejas (ranking del Sprint 4) puede ser necesario `$queryRaw`.
