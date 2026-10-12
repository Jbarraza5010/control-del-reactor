# control-del-reactor
Control del Reactor: juego multijugador en tiempo real donde los jugadores compiten por la energía de un reactor central usando paneles de botones físicos.

CE-1105 Principios de Modelado en Ingeniería · TEC · II Semestre 2026

## Tecnologías

Cliente del juego: Godot Engine (GDScript). Backend de cuentas: Python 3.12 + FastAPI. Base de datos: PostgreSQL. Contenedores: Docker.

## Levantar el entorno (requiere Docker Desktop)

```
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Backend (API) | http://localhost:8000/health |
| Contrato de la API (Swagger) | http://localhost:8000/docs |
| Adminer (visor de BD) | http://localhost:8080 (sistema: PostgreSQL, servidor: `db`, usuario/clave/BD: `reactor`) |
| PostgreSQL | localhost:5432 |

Apagar: `docker compose down` · Borrar también los datos: `docker compose down -v`

Más detalle del backend en [`backend/README.md`](backend/README.md). Diagramas en [`docs/arquitectura`](docs/arquitectura) y decisiones en [`docs/adr`](docs/adr).
