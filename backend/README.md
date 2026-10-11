# Backend

Servidor de Control del Reactor: API REST (cuentas, perfil, ranking), canal de tiempo real (WebSocket) y gateway del hardware.

## Arquitectura por capas

```
api  →  application  →  domain  ←  infrastructure
```

| Carpeta | Responsabilidad |
|---|---|
| `src/api/` | Controladores y rutas REST/WebSocket. Validan la entrada y llaman a `application`. Sin lógica de negocio. |
| `src/application/` | Servicios / casos de uso (`AuthService`, `ProfileService`, `DeviceLinkService`…). Orquestan el dominio. |
| `src/domain/` | Entidades, reglas de negocio e **interfaces** de repositorio. No depende de ninguna otra capa. |
| `src/infrastructure/persistence/` | Implementaciones de los repositorios con PostgreSQL (patrón **Repository**). |
| `src/infrastructure/email/` | Envío de correos de verificación y recuperación. |
| `src/infrastructure/hardware/` | Gateway del panel físico: recibe los eventos del Arduino (patrones **Adapter** / **Observer**). |
| `src/shared/` | Manejo de errores, configuración y logging. |
| `migrations/` | Migraciones versionadas y reversibles de la base de datos. |
| `tests/unit/` | Pruebas unitarias (dominio y servicios). |
| `tests/integration/` | Pruebas contra PostgreSQL real en contenedor. |

**Regla:** las dependencias apuntan hacia `domain`. `infrastructure` implementa interfaces definidas en `domain`, y `domain` nunca importa nada de `infrastructure` ni de `api`.

> El stack definitivo (lenguaje y framework) se documenta en `docs/adr/0001-stack-backend.md`.
