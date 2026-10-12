# Control del Reactor

**Battle Arena Challenge** — CE-1105 Principios de Modelado en Ingeniería · Instituto Tecnológico de Costa Rica · II Semestre 2026

Control del Reactor es un juego multijugador en tiempo real. Los jugadores compiten por la energía de un reactor central y se controlan con paneles de botones físicos (Arduino).

## Estructura del repositorio

| Carpeta | Contenido | Responsable (Sprint 2) |
|---|---|---|
| `backend/` | Servidor: API REST, tiempo real, lógica de dominio y persistencia | Ulfrán (esqueleto) · Moisés (autenticación) |
| `backend/migrations/` | Migraciones versionadas de PostgreSQL | Moisés |
| `client/` | Cliente del juego en Godot (escritorio y móvil) | Jordanny |
| `hardware/` | Firmware del panel, simulador y contrato de mensajes | Javier |
| `docs/` | Diagramas, ADRs, contrato de la API y documentación de pruebas | Todos |
| `.github/` | Pipeline de CI y plantilla de Pull Request | Javier |
| `docker-compose.yml` | Levanta el entorno completo con Docker | Ulfrán |

## Tareas del Sprint 2 (entrega: 22 de octubre, 2026)

Cada integrante trabaja en las carpetas indicadas. Si necesita tocar una carpeta de otra persona, el dueño de esa carpeta revisa el Pull Request.

### Jordanny — Cliente Godot y gestión

| Tarea | Carpeta / archivo |
|---|---|
| Crear el proyecto de Godot | `client/project.godot` |
| Pantalla de registro (US-001, US-002, US-003) | `client/scenes/auth/` |
| Pantalla de verificación de correo (US-004) | `client/scenes/auth/` |
| Pantalla de inicio de sesión (US-005) | `client/scenes/auth/` |
| Pantalla de recuperación de contraseña (US-007) | `client/scenes/auth/` |
| Pantalla de perfil (US-008) | `client/scenes/profile/` |
| Pantalla de vinculación del panel y botones presionados (US-013) | `client/scenes/hardware/` |
| Botones, campos y mensajes reutilizables | `client/scenes/common/` |
| Cliente HTTP/WebSocket que llama al backend | `client/scripts/services/` |
| Manejo de la sesión (token) y configuración | `client/scripts/autoload/` |
| Imágenes, fuentes y sonidos | `client/assets/sprites/`, `client/assets/fonts/`, `client/assets/sounds/` |
| Pruebas del cliente | `client/tests/` |
| Sprint Backlog, cronograma, riesgos, Wiki, bitácora y % de aporte | Azure DevOps (Boards y Wiki) |

### Moisés — Base de datos y autenticación

| Tarea | Carpeta / archivo |
|---|---|
| Diagrama del modelo de datos (jugadores, partidas, récords) | `docs/architecture/` |
| Migraciones de PostgreSQL (usuarios, tokens, dispositivos) | `backend/migrations/` |
| Entidades de usuario, perfil y tokens + interfaces de repositorio | `backend/src/domain/` |
| Repositorios PostgreSQL de usuarios y tokens | `backend/src/infrastructure/persistence/` |
| Servicios de registro, verificación, login y recuperación (US-001 a US-005, US-007) | `backend/src/application/` |
| Endpoints REST de autenticación y perfil | `backend/src/api/` |
| Envío de correos de verificación y recuperación | `backend/src/infrastructure/email/` |
| Login con Google (US-006, si da el tiempo) | `backend/src/application/`, `backend/src/api/` |
| Pruebas unitarias de sus servicios | `backend/tests/unit/` |
| Documentación de los endpoints | `docs/api/` |

### Ulfrán — Arquitectura y Docker

| Tarea | Carpeta / archivo |
|---|---|
| ADR del stack del backend | `docs/adr/0001-stack-backend.md` |
| Esqueleto del backend por capas (punto de entrada, inyección de dependencias) | `backend/src/` |
| Estructura base de controladores y rutas | `backend/src/api/` |
| Estructura base de servicios | `backend/src/application/` |
| Clases base del dominio y patrones (Factory, Observer) | `backend/src/domain/` |
| Clase base del patrón Repository | `backend/src/infrastructure/persistence/` |
| Manejo global de errores, configuración y logging | `backend/src/shared/` |
| Dockerfile del backend | `backend/Dockerfile` |
| Docker Compose (backend + PostgreSQL + Mailpit) y variables | `docker-compose.yml`, `.env.example` |
| Vistas lógica, de componentes y de despliegue | `docs/architecture/` |
| Demás ADRs (protocolo de hardware, autenticación) | `docs/adr/` |
| Revisar los Pull Requests de backend | — |

### Javier — Repositorio, hardware, CI y pruebas

| Tarea | Carpeta / archivo |
|---|---|
| Repositorio, estrategia de ramas y README | `README.md` |
| Plantilla de Pull Request | `.github/pull_request_template.md` |
| Pipeline de CI (build + pruebas automáticas) | `.github/workflows/ci.yml` |
| Protocolo de mensajes del panel | `hardware/PROTOCOL.md` |
| Firmware del Arduino (5 botones) | `hardware/firmware/arduino/` |
| Puente serial PC → backend | `hardware/bridge/` |
| Simulador del panel | `hardware/simulator/` |
| Gateway del panel en el backend y vinculación (US-013) | `backend/src/infrastructure/hardware/` |
| ADR del protocolo de hardware | `docs/adr/` |
| Pruebas de integración (API + PostgreSQL) | `backend/tests/integration/` |
| Plan de pruebas | `docs/testing/plan-de-pruebas.md` |
| Casos de prueba por historia de usuario | `docs/testing/casos-US-XXX.md` |

> **Todos:** hacer pruebas unitarias de su propio código, revisar Pull Requests de otro integrante, registrar horas en la bitácora y participar en la demo del MVP.

## Cómo levantar el entorno

```bash
cp .env.example .env      # ajustar valores locales
docker compose up -d      # PostgreSQL + Mailpit (y el backend cuando esté listo)
```

- PostgreSQL: `localhost:5432`
- Mailpit (bandeja de correos de prueba): http://localhost:8025

## Estrategia de ramas

| Rama | Uso |
|---|---|
| `main` | Versión entregable. Solo recibe merges desde `develop` o `hotfix/*`. |
| `develop` | Integración del equipo. Merge solo por Pull Request con 1 aprobación y CI en verde. |
| `feature/"US-XXX-descripcion"` | Una rama por historia o tarea. Nace de `develop`. |

**Commits:** mensajes descriptivos que mencionen el work item de Azure Boards, por ejemplo:

```
feat(auth): valida correo único en el registro AB#123
```

## Enlaces

- Azure DevOps (Boards y Wiki): https://dev.azure.com/ModeladoIIS2026/Proyecto%20Control%20del%20Reactor

## Equipo

| Integrante | Rol |
|---|---|
| Jordanny Hernández Mora | Scrum Master / Product Owner del equipo |
| Moisés Barboza Rojas | Analista de Requisitos |
| Ulfrán Rodríguez Cordero | Arquitecto de Software |
| Javier Alejandro Barraza Arias | Analista de Procesos y Calidad |
