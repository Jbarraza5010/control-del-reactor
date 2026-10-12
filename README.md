# Control del Reactor (Battle Arena Challenge)

CE-1105 Principios de Modelado en Ingeniería · TEC · II Semestre 2026

## Levantar el entorno (requiere Docker Desktop)

```
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Backend (API) | http://localhost:3000/health |
| Adminer (visor de BD) | http://localhost:8080 (sistema: PostgreSQL, servidor: `db`, usuario/clave/BD: `reactor`) |
| PostgreSQL | localhost:5432 |

Apagar: `docker compose down` · Borrar también los datos: `docker compose down -v`

Más detalle del backend en [`backend/README.md`](backend/README.md).
