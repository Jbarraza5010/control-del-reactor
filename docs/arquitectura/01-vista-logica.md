# Vista lógica — Sprint 2

Actualiza la vista lógica de la ERS (sección 7.1) con lo que realmente se construye en el Sprint 2:
el backend de cuentas organizado en capas. Los elementos con línea punteada son del roadmap (Sprint 3 en adelante).

```mermaid
flowchart TB
  subgraph CLI["Capa de presentación (clientes)"]
    GODOT["Cliente Godot (escritorio / móvil)"]
    SIM["Simulador del panel de 5 botones"]
  end

  subgraph API["Backend - presentation/http"]
    ROUTES["Rutas y controladores<br/>(/health, /api/v1/auth)"]
    MW["Middlewares<br/>(errorHandler, notFound)"]
  end

  subgraph APP["Backend - application"]
    SVC["Servicios de cuentas<br/>(Moisés: registro, verificación, login, recuperación)"]
    PORTS["Puertos<br/>(Mailer, DatabaseHealth)"]
    LISTEN["registerMailListeners"]
  end

  subgraph DOM["Backend - domain"]
    ENT["Entidades<br/>(User)"]
    REPO["Contratos de repositorio<br/>(UserRepository)"]
  end

  subgraph INFRA["Backend - infrastructure"]
    PRISMA["PrismaUserRepository"]
    MEM["InMemoryUserRepository (pruebas)"]
    MAIL["MailerFactory -> ConsoleMailer / SmtpMailer"]
  end

  subgraph SHARED["Backend - shared"]
    BUS["EventBus (Observer)"]
    ERR["AppError y subclases"]
  end

  DB[("PostgreSQL")]

  GODOT -->|"HTTP/JSON"| ROUTES
  SIM -.->|"Sprint 3: protocolo de hardware"| ROUTES
  ROUTES --> MW
  ROUTES --> SVC
  SVC --> REPO
  SVC --> ENT
  SVC --> BUS
  BUS --> LISTEN
  LISTEN --> PORTS
  PRISMA -.->|"implementa"| REPO
  MEM -.->|"implementa"| REPO
  MAIL -.->|"implementa"| PORTS
  PRISMA --> DB
  SVC -.-> ERR

  MOTOR["Motor de partida (Godot host, LAN)"]:::future
  REDIS["Redis / MQTT / WebSocket"]:::future
  MOTOR -.-> API
  REDIS -.-> API

  classDef future stroke-dasharray: 5 5,fill:#f4f4f4,color:#555;
```

**Regla de dependencia:** `presentation → application → domain`; `infrastructure` implementa las interfaces de `domain` y `application`.
`domain` no importa Express ni Prisma.
