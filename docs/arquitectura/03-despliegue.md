# Vista de despliegue — Sprint 3

Demostración local con Docker Compose y partida en red de área local (ADR-009). La versión cloud con balanceador,
Redis y registro de contenedores de la ERS (sección 7.2) sigue para el Sprint 5 (ADR-007).

```mermaid
flowchart TB
  subgraph LAN["Red local (Wi-Fi o switch)"]
    subgraph PCA["PC del anfitrión (Windows 11 + Docker Desktop)"]
      GODA["Cliente Godot - anfitrión<br/>(fuera de Docker) UDP 7777"]
      BRA["Puente del panel 1"]
      subgraph COMPOSE["docker compose - proyecto control-del-reactor"]
        BACK["reactor-backend<br/>python:3.12-slim - puerto 8000"]
        DBC["reactor-db<br/>postgres:16-alpine - puerto 5432"]
        ADM["reactor-adminer<br/>adminer:4 - puerto 8080"]
        VOL[("volumen pgdata")]
      end
    end

    subgraph PCB["PC del jugador 2"]
      GODB["Cliente Godot"]
      BRB["Puente del panel 2"]
    end

    subgraph MOV["Celular Android (opcional)"]
      GODM["Cliente Godot móvil"]
    end
  end

  GODB -->|"UDP 7777"| GODA
  GODM -->|"UDP 7777"| GODA
  GODA -->|"http://localhost:8000"| BACK
  BRA -->|"http://localhost:8000"| BACK
  BRB -->|"http://IP-anfitrión:8000"| BACK
  GODB -->|"http://IP-anfitrión:8000"| BACK
  BACK -->|"postgresql://db:5432"| DBC
  ADM --> DBC
  DBC --- VOL
```

**Arranque de la demo**

1. En la PC del anfitrión: `docker compose up --build` y abrir el puerto UDP 7777 en el firewall de Windows.
2. Cada jugador conecta su panel y ejecuta su puente apuntando a la IP del anfitrión (según `hardware/README.md`).
3. El anfitrión crea la partida desde «Jugar»; los demás se unen por IP o código.
4. Al terminar, el anfitrión envía el resultado al backend y se actualiza el ranking.

| Servicio | Imagen | Puerto | Healthcheck |
|---|---|---|---|
| db | postgres:16-alpine | 5432 | `pg_isready` |
| backend | build de `./backend` (multi-stage) | 8000 | `GET /health` |
| adminer | adminer:4 | 8080 | — |
| Partida (Godot anfitrión) | no corre en Docker | UDP 7777 | — |
