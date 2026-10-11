# Cliente (Godot)

Cliente del juego para escritorio y móvil (Godot exporta a Android desde este mismo proyecto).

> Crear aquí el proyecto de Godot (`project.godot`) desde el editor, usando esta carpeta como raíz.

| Carpeta | Contenido |
|---|---|
| `scenes/auth/` | Registro, login, verificación de correo, recuperación de contraseña |
| `scenes/profile/` | Perfil del jugador |
| `scenes/hardware/` | Vinculación del panel y visualización de botones presionados |
| `scenes/common/` | Componentes de UI reutilizables |
| `scripts/services/` | Cliente HTTP / WebSocket hacia el backend (`api_client.gd`) |
| `scripts/autoload/` | Singletons: sesión (token), configuración |
| `assets/` | `sprites/`, `fonts/`, `sounds/` |
| `tests/` | Pruebas del cliente (por ejemplo, con GUT) |

El contrato de la API que consume el cliente está en `docs/api/`.
