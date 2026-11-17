# Diagrama de componentes — Sprint 3

```mermaid
flowchart LR
  subgraph PCH["PC del anfitrión"]
    subgraph GH["Cliente Godot (anfitrión)"]
      UIH["Escenas / HUD<br/>(Jordanny)"]
      NETH["Red ENet<br/>(Javier)"]
      MOT["Motor de partida<br/>(Ulfrán)"]
      PANH["PanelHardware"]
    end
    BRH["Puente serial<br/>(Javier)"]
    subgraph BACK["Contenedor: backend (Python 3.12 + FastAPI)"]
      HTTP["API REST + WebSocket<br/>/auth  /hardware  /docs"]
      AUTH["Cuentas<br/>(Moisés)"]
      HW["Panel físico<br/>(Javier)"]
      BUS["EventBus (Observer)"]
      REPOS["Repositorios (Repository)"]
    end
    DB[("PostgreSQL 16")]
  end

  subgraph PC2["PC o celular del jugador 2"]
    G2["Cliente Godot<br/>(solo entrada y dibujo)"]
    BR2["Puente serial"]
  end

  PAN1["Panel físico 1<br/>(Arduino)"]
  PAN2["Panel físico 2<br/>(Arduino)"]

  PAN1 -->|"USB serial"| BRH
  PAN2 -->|"USB serial"| BR2
  BRH -->|"HTTP"| HTTP
  BR2 -->|"HTTP"| HTTP
  PANH -->|"WebSocket"| HTTP
  G2 -->|"entrada (UDP 7777)"| NETH
  NETH -->|"instantáneas y eventos"| G2
  NETH --> MOT
  UIH --> MOT
  MOT -->|"resultado (HTTP)"| HTTP
  HTTP --> AUTH
  HTTP --> HW
  AUTH --> REPOS
  AUTH --> BUS
  HW --> BUS
  REPOS --> DB
```

| Componente | Responsable | Estado Sprint 3 |
|---|---|---|
| Motor de partida (estados, guardianes, obstáculos, eventos, puntuación, fin) | Ulfrán | Implementado y con pruebas |
| Arena, escenarios, HUD y ceremonia | Jordanny | Por integrar con el motor |
| Red del juego, panel dentro de la partida, reactor, terminales | Javier | Por integrar con el motor |
| Resultados, ranking, historial, logros | Moisés | Por recibir el `ResultadoPartida` |
| API REST, errores, EventBus, repositorios | Ulfrán | Estable desde el Sprint 2 |
