# ADR-001 — Backend con Python 3.12 + FastAPI (cliente en Godot)

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La ERS (sección 7) propone una arquitectura de referencia "en el lenguaje de GDScript (muy similar a Python)" y, en 7.4,
lista para el backend GDScript, Node.js (NestJS) o .NET. El equipo decidió trabajar con **Godot Engine** para el cliente
y **Python** para el backend, de modo que todos usen una sintaxis parecida a GDScript.
El Sprint 2 exige cuentas (registro, verificación de correo, inicio de sesión, recuperación) sobre PostgreSQL, con Docker y CI.

## Decisión
Python 3.12 con FastAPI (servidor ASGI uvicorn) para la API REST de cuentas. El cliente Godot (GDScript) la consume por HTTP/JSON.

## Alternativas consideradas
- **Node.js + Express/NestJS:** figura en la ERS 7.4, pero el equipo no lo usa; se descartó para no mezclar tres lenguajes.
- **Flask:** más simple, pero no trae validación de entrada ni documentación de la API; habría que agregarlas a mano.
- **Django:** completo, pero impone su propio ORM y estructura, y chocaría con la arquitectura por capas (ADR-002).
- **GDScript como backend:** no tiene ecosistema maduro para PostgreSQL, autenticación, correo ni migraciones.

## Consecuencias
- (+) Un lenguaje de sintaxis cercana a GDScript para todo el equipo.
- (+) FastAPI valida las entradas con pydantic y publica el contrato de la API en `/docs` (Swagger), útil para que el cliente Godot sepa qué llamar.
- (+) Ecosistema maduro: SQLAlchemy, Alembic, pytest, smtplib.
- (−) Python no figura literalmente en la lista de la sección 7.4 de la ERS; es coherente con su intención (sintaxis tipo Python) y se documenta aquí. Se recomienda confirmarlo con el docente.
- (−) Python no impone estructura: la disciplina de capas se mantiene con revisión de Pull Requests.
