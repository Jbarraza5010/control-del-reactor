# Vista lógica — Sprint 2

Actualiza la vista lógica de la ERS (sección 7.1) con lo que realmente se construye en el Sprint 2:
el backend de cuentas en Python organizado en capas. Los elementos con línea punteada son del roadmap (Sprint 3 en adelante).

```mermaid
flowchart TB
  subgraph CLI["Capa de presentación (clientes)"]
    GODOT["Cliente Godot (GDScript, escritorio / móvil)"]
    SIM["Simulador del panel de 5 botones"]
  end

  subgraph API["Backend - presentation/api (FastAPI)"]
    ROUTES["Rutas<br/>(/health, /api/v1/auth)"]
    ERRH["Manejadores de error<br/>(AppError a JSON)"]
  end

  subgraph APP["Backend - application"]
    SVC["Servicios de cuentas<br/>(Moisés: registro, verificación, login, recuperación)"]
    PORTS["Puertos<br/>(Mailer, DatabaseHealth)"]
    LISTEN["register_mail_listeners"]
  end

  subgraph DOM["Backend - domain"]
    ENT["Entidades<br/>(User)"]
    REPO["Contratos de repositorio<br/>(UserRepository)"]
  end

  subgraph INFRA["Backend - infrastructure"]
    SQL["SqlUserRepository (SQLAlchemy)"]
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
  ROUTES --> ERRH
  ROUTES --> SVC
  SVC --> REPO
  SVC --> ENT
  SVC --> BUS
  BUS --> LISTEN
  LISTEN --> PORTS
  SQL -.->|"implementa"| REPO
  MEM -.->|"implementa"| REPO
  MAIL -.->|"implementa"| PORTS
  SQL --> DB
  SVC -.-> ERR

  MOTOR["Motor de partida (Godot host, LAN)"]:::future
  REDIS["Redis / MQTT / WebSocket"]:::future
  MOTOR -.-> API
  REDIS -.-> API

  classDef future stroke-dasharray: 5 5,fill:#f4f4f4,color:#555;
```

**Regla de dependencia:** `presentation → application → domain`; `infrastructure` implementa las interfaces de `domain` y `application`.
`domain` no importa FastAPI ni SQLAlchemy.
