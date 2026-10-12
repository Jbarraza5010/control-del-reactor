# Diagrama de componentes — Sprint 2

```mermaid
flowchart LR
  subgraph Cliente["Equipo del jugador"]
    GODOT["Cliente Godot<br/>(Jordanny)"]
    SIM["Simulador de panel<br/>(Javier)"]
  end

  subgraph Backend["Contenedor: backend (Node.js 20 + TypeScript + Express)"]
    HTTP["API REST<br/>/health  /api/v1/auth"]
    AUTH["Módulo de cuentas<br/>(Moisés)"]
    ERRS["Manejo de errores<br/>AppError + errorHandler"]
    BUS["EventBus<br/>(Observer)"]
    MAILF["MailerFactory<br/>(Factory)"]
    REPOS["Repositorios<br/>(Repository)"]
    PRISMA["Prisma Client"]
  end

  DB[("PostgreSQL 16")]
  SMTP["Servidor SMTP<br/>(producción)"]
  LOG["Log del backend<br/>(desarrollo)"]
  ADM["Adminer<br/>(visor de BD)"]

  GODOT -->|"HTTP/JSON"| HTTP
  SIM -.->|"Sprint 3"| HTTP
  HTTP --> AUTH
  HTTP --> ERRS
  AUTH --> REPOS
  AUTH --> BUS
  BUS --> MAILF
  REPOS --> PRISMA
  PRISMA -->|"SQL"| DB
  MAILF -->|"MAIL_TRANSPORT=smtp"| SMTP
  MAILF -->|"MAIL_TRANSPORT=console"| LOG
  ADM --> DB
```

| Componente | Responsable | Estado Sprint 2 |
|------------|-------------|-----------------|
| API REST, errores, EventBus, MailerFactory, repositorios | Ulfrán | Esqueleto listo |
| Módulo de cuentas (servicios de registro, verificación, login, recuperación) | Moisés | En desarrollo |
| Cliente Godot | Jordanny | En desarrollo |
| Simulador de panel y protocolo de hardware | Javier | En desarrollo |
