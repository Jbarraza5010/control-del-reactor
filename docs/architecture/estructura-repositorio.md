# Estructura del repositorio

- **Proyecto:** Control del Reactor (Battle Arena Challenge)
- **Sprint:** 2
- **Responsable:** Javier Alejandro Barraza Arias
- **Última actualización:** 2026-10-10

## 1. Propósito

Este documento describe cómo se distribuye el repositorio, así como la justificación de las diferentes decisiones tomadas a la hora de diseñar la organización del mismo.

## 2. Vista general

```
control-del-reactor/
├── .github/                   # Pipeline de CI y plantilla de Pull Request
│   ├── workflows/ci.yml
│   └── pull_request_template.md
│
├── backend/                   # Servidor: API REST, tiempo real, dominio y persistencia
│   ├── src/
│   │   ├── api/               # Controladores / rutas REST y WebSocket
│   │   ├── application/       # Servicios / casos de uso
│   │   ├── domain/            # Entidades, reglas de negocio, interfaces de repositorio
│   │   ├── infrastructure/
│   │   │   ├── persistence/   # Repositorios PostgreSQL
│   │   │   ├── email/         # Envío de correos
│   │   │   └── hardware/      # Gateway del panel físico
│   │   └── shared/            # Errores, configuración, logging
│   ├── migrations/            # Migraciones versionadas de la base de datos
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── Dockerfile
│
├── client/                    # Cliente del juego en Godot (escritorio y móvil)
│   ├── scenes/                # auth/, profile/, hardware/, common/
│   ├── scripts/               # services/, autoload/
│   ├── assets/                # sprites/, fonts/, sounds/
│   └── tests/
│
├── hardware/                  # Panel físico de botones (Arduino)
│   ├── firmware/arduino/      # Código del Arduino
│   ├── bridge/                # Puente serial PC → backend
│   ├── simulador/             # Simulador del panel
│   └── PROTOCOL.md            # Contrato de mensajes
│
├── docs/                      # Documentación versionada
│   ├── architecture/          # Vistas de arquitectura y diagramas
│   ├── adr/                   # Decisiones técnicas (ADR)
│   ├── api/                   # Contrato de la API REST
│   └── testing/               # Plan y casos de prueba
│
├── docker-compose.yml         # Entorno completo: PostgreSQL + Mailpit (+ backend)
├── .env.example               # Variables de entorno de referencia (sin secretos)
├── .gitignore
└── README.md
```

## 3. Decisión principal: un solo repositorio 

Todo el proyecto (backend, cliente, hardware y documentación) vive en un único repositorio, con una carpeta por componente.

### Por qué

| Razón | Explicación |
|---|---|
| **Equipo pequeño** | Con 4 integrantes, administrar varios repositorios agrega trabajo sin beneficio real. |
| **Cambios que van juntos** | Un cambio en la API normalmente afecta al backend y al cliente al mismo tiempo. En un solo repo se hace en un único Pull Request y se revisa completo. |
| **Un solo pipeline de CI** | Un único flujo construye y prueba todos los componentes, como pide el enunciado (build automático y pruebas automáticas). |
| **Versión única del producto** | Una etiqueta (por ejemplo `v0.1.0`) identifica exactamente qué versión de cada componente se entregó en cada Sprint. |
| **Historial verificable** | El profesor puede revisar en un solo lugar los commits y aportes de todo el equipo. |

### Alternativa descartada

**Un repositorio por componente** (backend, cliente, hardware por separado). Se descartó porque obliga a coordinar versiones entre repos, duplica la configuración de CI y dificulta ver el trabajo del equipo en conjunto. Tendría sentido en un equipo grande o con componentes que se despliegan de forma independiente por equipos distintos.

## 4. Criterios con los que se dividió

1. **Por componente del sistema.** Cada carpeta principal corresponde a una pieza de la arquitectura propuesta en el ERS: `client/` (presentación), `backend/` (comunicación, aplicación/dominio y persistencia) y `hardware/` (dispositivo físico).
2. **Un dueño por carpeta.** Cada integrante tiene un área principal para el Sprint 2 (ver el `README.md`). Esto reduce conflictos de merge y deja claro quién revisa cada Pull Request.
3. **Código, infraestructura y documentación separados.** El código va en su componente, la infraestructura (Docker, variables, CI) en la raíz y en `.github/`, y la documentación técnica en `docs/`.
4. **Preparado para crecer.** La estructura ya contempla lo que se agregará en los Sprints siguientes sin tener que reorganizar.

## 5. Detalle por carpeta

### 5.1 `backend/`: arquitectura por capas

El backend sigue una arquitectura por capas, interactuando con el resto del sistema de la siguiente forma:

```
api  →  application  →  domain  ←  infrastructure
```

| Capa | Responsabilidad | Por qué separada |
|---|---|---|
| `api/` | Recibe las peticiones, valida la entrada y responde | La forma de comunicarse (REST, WebSocket) puede cambiar sin tocar la lógica |
| `application/` | Orquesta los casos de uso (registro, login, vincular panel…) | Cada caso de uso queda en un lugar identificable y fácil de probar |
| `domain/` | Entidades y reglas de negocio (correo único, penalizaciones…) | Es el corazón del sistema; no depende de bases de datos ni frameworks |
| `infrastructure/` | Implementa lo técnico: PostgreSQL, correo, hardware | Permite cambiar una tecnología sin afectar el dominio |
| `shared/` | Errores, configuración y logging comunes | Evita duplicar código entre capas (principio DRY) |

**Regla de dependencias:** las dependencias apuntan hacia `domain`. `infrastructure` implementa interfaces definidas en `domain`, y `domain` nunca importa nada de las otras capas. Esto aplica el principio de inversión de dependencias (SOLID) y facilita las pruebas, porque el dominio se prueba sin base de datos.

**Patrones de diseño y dónde viven:**

| Patrón | Tipo | Ubicación |
|---|---|---|
| Repository | Estructural / arquitectónico | `infrastructure/persistence/` (implementación) + interfaces en `domain/` |
| Adapter | Estructural | `infrastructure/hardware/`: adapta los mensajes del panel al modelo del dominio |
| Observer | Comportamiento | Eventos del panel hacia sus suscriptores (y, más adelante, puntajes en tiempo real) |
| Factory | Creacional | `domain/`: creación de manejadores de comandos y, más adelante, guardianes y eventos |

**Otras decisiones:**

- `migrations/` dentro de `backend/`: las migraciones pertenecen al backend porque es el único componente que accede a la base de datos. Así un cambio de esquema viaja en el mismo Pull Request que el código que lo usa.
- `tests/unit/` y `tests/integration/` separados: las unitarias son rápidas y no necesitan servicios externos; las de integración usan PostgreSQL en un contenedor. Separarlas permite correrlas por aparte en el pipeline.
- Módulos dentro de cada capa: dentro de `domain/`, `application/` y `api/` cada funcionalidad tiene su módulo (`auth`, `profile`, `device`). Así dos integrantes pueden trabajar en la misma capa sin editar los mismos archivos.

### 5.2 `client/`: cliente Godot

| Carpeta | Por qué |
|---|---|
| `scenes/` organizada por funcionalidad (`auth/`, `profile/`, `hardware/`, `common/`) | Encontrar una pantalla es inmediato y cada funcionalidad crece en su propia carpeta |
| `scripts/services/` | La comunicación con el backend queda en un solo lugar; las pantallas no hacen peticiones HTTP directamente |
| `scripts/autoload/` | Datos globales (sesión, token, configuración) disponibles en todo el juego mediante singletons de Godot |
| `assets/` | Recursos gráficos y de sonido separados del código |

Godot puede exportar a Android desde el mismo proyecto, por lo que no se creó una carpeta aparte para la aplicación móvil. Si más adelante se decide usar otra tecnología para móvil, se agregaría una carpeta `mobile/`.

### 5.3 `hardware/`: panel físico (Arduino)

| Carpeta / archivo | Por qué |
|---|---|
| `firmware/arduino/` | Código que corre en el Arduino: lee los 5 botones y envía los eventos por puerto serial |
| `bridge/` | El Arduino se conecta por USB y el backend corre dentro de Docker, desde donde no puede leer el puerto serial de la PC. El puente corre en la PC, lee el puerto serial y reenvía los eventos al backend |
| `simulador/` | Permite desarrollar y probar sin el hardware real. Emite exactamente los mismos mensajes que el Arduino, siguiendo la recomendación del enunciado de probar temprano la comunicación con el hardware o su simulación |
| `PROTOCOL.md` | Contrato único de mensajes. El firmware, el puente, el simulador y el backend se basan en él, así que cualquiera de las piezas se puede cambiar sin romper las demás |

### 5.4 `docs/`: documentación versionada

La documentación oficial está en la Wiki de Azure DevOps. En `docs/` se guardan los archivos que conviene versionar junto al código: los diagramas editables, los ADRs, el contrato de la API y la documentación de pruebas. Así queda registrado en Git quién cambió cada documento y cuándo, y la Wiki enlaza a ellos.

| Carpeta | Contenido |
|---|---|
| `architecture/` | Vistas de arquitectura, diagramas y este documento |
| `adr/` | Una decisión técnica por archivo (stack, protocolo, autenticación…) |
| `api/` | Endpoints, formatos de request/respuesta y errores |
| `testing/` | Plan de pruebas y casos de prueba por historia de usuario |

Cada carpeta incluye una plantilla `.md` para mantener un formato uniforme.

### 5.5 Raíz y `.github/`

| Archivo | Por qué en la raíz |
|---|---|
| `docker-compose.yml` | Levanta el entorno completo (PostgreSQL, Mailpit y luego el backend) con un solo comando. Involucra a varios componentes, así que no pertenece a ninguno en particular |
| `.env.example` | Lista las variables de entorno sin exponer secretos. Cada integrante lo copia a `.env`, que no se sube al repositorio |
| `.gitignore` | Reglas de Godot, backend, Arduino, editores y el archivo `.env` |
| `README.md` | Punto de entrada: qué es el proyecto, cómo levantarlo, estrategia de ramas y tareas del Sprint |
| `.github/` | GitHub lee el pipeline de CI y la plantilla de Pull Request desde esta ruta fija |

## 6. Convenciones

- **Carpetas vacías:** contienen un archivo `.gitkeep` para que Git las guarde. Se puede borrar cuando la carpeta ya tenga archivos reales.
- **Ramas:** `feature/US-XXX-descripcion`, que nace de `develop` y vuelve a `develop` por Pull Request.
- **Commits:** mensajes descriptivos que mencionan el work item de Azure Boards (`AB#123`).
- **Módulos del backend:** cada funcionalidad usa el mismo nombre en todas las capas (`auth`, `profile`, `device`).

## 7. Evolución prevista

| Sprint | Cambios esperados en la estructura |
|---|---|
| Sprint 3 | Nuevos módulos en el backend (`match`, `ranking`, `events`), nuevas escenas en el cliente (`scenes/arena/`, `scenes/victory/`) y despliegue cloud en una carpeta `infra/` si hace falta |
| Si cambia la tecnología móvil | Nueva carpeta `mobile/` en la raíz |

Cualquier cambio importante a esta estructura se documenta en este archivo y, si es una decisión relevante, en un ADR.
