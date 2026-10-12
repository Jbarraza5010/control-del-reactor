# Backend — Control del Reactor (Sprint 2)

API REST de cuentas: Python 3.12 + FastAPI, SQLAlchemy 2 + Alembic, PostgreSQL.
El cliente del juego es Godot (GDScript) y consume esta API por HTTP/JSON.

## Arquitectura por capas

```
app/
├── config.py             Variables de entorno validadas
├── presentation/api/     FastAPI: rutas, manejadores de error (HTTP aquí y solo aquí)
├── application/          Casos de uso (services) y puertos (interfaces hacia afuera)
├── domain/               Entidades y contratos de repositorio. Python puro
├── infrastructure/       Implementaciones: SQLAlchemy, memoria, correo
├── shared/               Errores, eventos (EventBus), logger
├── container.py          Composition root (inyección de dependencias)
└── main.py               create_app(): fábrica de la aplicación
alembic/                  Migraciones de la base de datos
tests/                    Pruebas con pytest
```

Regla de dependencia: `presentation -> application -> domain` y `infrastructure -> domain/application`.
El dominio no importa nada de FastAPI ni de SQLAlchemy.

## Patrones de diseño aplicados

| Patrón | Dónde | Para qué |
|--------|-------|----------|
| Repository | `domain/repositories/user_repository.py` + `infrastructure/persistence/{sql,memory}` | El dominio no conoce PostgreSQL; las pruebas usan la versión en memoria |
| Factory | `infrastructure/mail/mailer_factory.py` | Elige ConsoleMailer o SmtpMailer según `MAIL_TRANSPORT` |
| Observer | `shared/events.py` (EventBus) + `application/services/register_mail_listeners.py` | Registrar un usuario dispara el correo sin acoplar ambos |
| Inyección de dependencias | `container.py` | Único lugar que elige implementaciones concretas |

## Manejo de errores

Las capas internas lanzan subclases de `AppError` (`ValidationAppError`, `ConflictError`, `UnauthorizedError`, `NotFoundError`...).
`presentation/api/error_handlers.py` las convierte en `{ "error": { "code", "message", "details" } }`.
Un error de validación devuelve 400; un error inesperado, un 500 genérico y el detalle solo queda en el log.

## Correr sin Docker

```
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
pytest                          # pruebas (no necesitan PostgreSQL)
```

Con Docker (`docker compose up --build`, desde la raíz del repo) el contrato de la API se ve en http://localhost:8000/docs
