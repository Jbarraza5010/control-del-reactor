# Vista de despliegue — Sprint 2

Versión local con Docker Compose. La versión cloud con balanceador, Redis y registro de contenedores
de la ERS (sección 7.2) queda para el Sprint 3 (ver ADR-007).

```mermaid
flowchart TB
  subgraph PC["Computadora del integrante (Windows 11 + Docker Desktop)"]
    GODOT["Cliente Godot<br/>(se ejecuta fuera de Docker)"]
    BROWSER["Navegador"]

    subgraph COMPOSE["docker compose  -  proyecto control-del-reactor"]
      BACK["reactor-backend<br/>imagen node:20-bookworm-slim<br/>puerto 3000"]
      DBC["reactor-db<br/>imagen postgres:16-alpine<br/>puerto 5432"]
      ADM["reactor-adminer<br/>imagen adminer:4<br/>puerto 8080"]
      VOL[("volumen pgdata")]
    end
  end

  GODOT -->|"http://localhost:3000"| BACK
  BROWSER -->|"http://localhost:8080"| ADM
  BACK -->|"postgresql://db:5432"| DBC
  ADM --> DBC
  DBC --- VOL
```

**Arranque:** `docker compose up --build`. El backend espera a que PostgreSQL esté saludable (`pg_isready`),
aplica las migraciones (`prisma migrate deploy`) y recién entonces inicia.

| Servicio | Imagen | Puerto | Healthcheck |
|----------|--------|--------|-------------|
| db | postgres:16-alpine | 5432 | `pg_isready` |
| backend | build de `./backend` (multi-stage) | 3000 | `GET /health` |
| adminer | adminer:4 | 8080 | — |
