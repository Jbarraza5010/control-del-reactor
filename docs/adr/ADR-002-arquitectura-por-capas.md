# ADR-002 — Arquitectura por capas con dependencia hacia el dominio

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La DoD (sección 8.1 de la ERS) exige código conforme a la arquitectura por capas, SOLID y Clean Code, y pruebas unitarias
con cobertura mínima del 70 % en la lógica de dominio. Cuatro personas escriben código a la vez y necesitan no pisarse.

## Decisión
Se organiza `backend/app` en: `presentation/api` (HTTP), `application` (casos de uso y puertos), `domain` (entidades y contratos),
`infrastructure` (SQLAlchemy, correo), `shared` (errores, eventos, logger) y `config.py`.
Las dependencias apuntan hacia adentro: `presentation → application → domain`; `infrastructure` implementa interfaces.
Los componentes se conectan en un único composition root (`app/container.py`).

## Alternativas consideradas
- **Carpetas por tipo técnico (routers/, models/, services/):** más simple, pero mezcla reglas de negocio con FastAPI y SQLAlchemy, y dificulta probar sin base de datos.
- **Un servicio por funcionalidad (microservicios):** innecesario para el alcance y multiplicaría los contenedores y el trabajo de despliegue.

## Consecuencias
- (+) La lógica de cuentas se prueba con repositorios en memoria, sin PostgreSQL.
- (+) Moisés trabaja en `application/` y `infrastructure/persistence`; Jordanny solo ve el contrato HTTP.
- (−) Hay más archivos y se necesita disciplina: los PR de backend se revisan verificando que `domain` no importe FastAPI ni SQLAlchemy.
