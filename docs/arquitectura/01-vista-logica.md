# Vista lógica — Sprint 3

Actualiza la vista del Sprint 2 con el **motor de partida** (cliente Godot, ejecutado por el anfitrión) y el
backend con sus rutas de panel físico. Las líneas punteadas son del roadmap (Sprint 4 en adelante).

```mermaid
flowchart TB
  subgraph CLI["Capa de presentación (clientes Godot: escritorio y Android)"]
    UI["Escenas y HUD<br/>(arena, tabla de posiciones, ceremonia)"]
    RED["Red del juego (ENet)<br/>lobby, entradas e instantáneas"]
    PANEL["PanelHardware<br/>(botones del panel físico)"]
  end

  subgraph MOTOR["Motor de partida (client/scripts/juego) - solo corre en el anfitrión"]
    PART["Partida<br/>(coordinador)"]
    JUG["ModeloJugador + State<br/>(normal, aturdido, escudado, eliminado)"]
    GUA["Guardian + Strategy<br/>(patrulla, persecución) + FabricaGuardianes"]
    OBS["Obstáculos<br/>(barrera móvil, puerta, trampa)"]
    EVT["Eventos especiales + FabricaEventos<br/>+ ProgramadorEventos"]
    MARC["Marcador + TablaPosiciones<br/>(Observer)"]
  end

  subgraph API["Backend - presentation/api (FastAPI)"]
    ROUTES["Rutas<br/>(/health, /api/v1/auth, /api/v1/hardware)"]
    HUB["hardware_hub (WebSocket)"]
  end

  subgraph APP["Backend - application"]
    SVC["Servicios<br/>(cuentas, panel físico)"]
    PORTS["Puertos<br/>(Mailer, DatabaseHealth, PlayerIdentity)"]
  end

  subgraph DOM["Backend - domain"]
    ENT["Entidades<br/>(User, AuthToken, HardwarePanel)"]
    REPO["Contratos de repositorio"]
  end

  subgraph INFRA["Backend - infrastructure"]
    SQL["Repositorios SQLAlchemy"]
    MEM["Repositorios en memoria (pruebas)"]
    MAIL["MailerFactory"]
  end

  BUS["EventBus (Observer)"]
  DB[("PostgreSQL")]

  UI --> PART
  RED --> PART
  PANEL --> RED
  PART --> JUG
  PART --> GUA
  PART --> OBS
  PART --> EVT
  PART --> MARC
  MARC -->|"señales"| UI

  PANEL -->|"HTTP + WebSocket"| ROUTES
  PART -->|"HTTP: resultado de la partida"| ROUTES
  ROUTES --> SVC
  ROUTES --> HUB
  SVC --> REPO
  SVC --> ENT
  SVC --> BUS
  BUS --> HUB
  SQL -.->|"implementa"| REPO
  MEM -.->|"implementa"| REPO
  MAIL -.->|"implementa"| PORTS
  SQL --> DB

  CLOUD["Despliegue en la nube / servidor dedicado"]:::future
  RED -.-> CLOUD

  classDef future stroke-dasharray: 5 5,fill:#f4f4f4,color:#555;
```

**Reglas de dependencia**

- Backend: `presentation → application → domain`; `infrastructure` implementa las interfaces. El dominio no importa FastAPI ni SQLAlchemy.
- Cliente: las escenas dependen del motor y nunca al revés. El motor no usa nodos de Godot, solo `RefCounted` y señales, por eso se prueba sin abrir el juego.
