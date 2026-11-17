# ADR-011: Eliminar el backend TypeScript heredado

- **Estado:** Aceptado
- **Fecha:** 2026-11-16
- **Autor(es):** Ulfrán Rodríguez Cordero (Arquitecto de Software)
- **Reemplaza parcialmente:** el esqueleto Node.js del Sprint 2 (commits `4878d7e` y siguientes del 11-oct)

## Contexto

En el Sprint 2 se empezó el backend con Node.js + TypeScript + Prisma. Después el equipo decidió usar Python 3.12 + FastAPI (ADR-001) porque el cliente es Godot y no se quería mezclar tres lenguajes, y el backend se migró (commit `e91e741`). Quedaron en `backend/` los archivos del esqueleto anterior, que ya no se construyen ni se ejecutan: el `Dockerfile` y `docker-compose.yml` solo usan Python.

Esos archivos duplican el backend de verdad (repositorios, EventBus, manejo de errores, pruebas) y confunden a quien lea el repositorio o configure el CI (por ejemplo, podría intentar correr `npm test`).

## Opciones consideradas

1. **Dejarlos como referencia.** Cero trabajo, pero deja dos backends en el repositorio y riesgo de que alguien modifique el equivocado.
2. **Moverlos a una rama de archivo.** Innecesario: el historial de Git ya conserva todo.
3. **Eliminarlos (elegida).**

## Decisión

Se eliminan: `backend/src/`, `backend/prisma/`, `backend/package.json`, `backend/package-lock.json`, `backend/tsconfig.json`, `backend/tsconfig.build.json`, `backend/vitest.config.ts` y las pruebas `backend/tests/*.test.ts`. Se conservan las pruebas de Python (`test_*.py`).

## Consecuencias

- (+) Un solo backend, un solo lenguaje y un solo conjunto de pruebas (`pytest`).
- (+) El pipeline de CI no necesita Node.js.
- (−) Quien quiera ver el esqueleto TypeScript debe buscarlo en el historial (`git show 4878d7e`).
- Pendiente: `backend/Estructura de Carpetas.txt` y `docs/architecture/estructura-repositorio.md` describen estructuras antiguas; conviene actualizarlos.
