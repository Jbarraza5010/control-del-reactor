# Modelo de datos de jugadores, partidas y estadísticas

Se conserva la migración original `0001`. Las revisiones siguientes añaden el modelo persistente requerido por cuentas y por el perfil del cliente:

| Revisión | Contenido |
|---|---|
| 0002 | Perfiles, tokens, partidas, participaciones, vista de récords e índices únicos de correo/usuario sin distinguir mayúsculas |
| 0003 | Identidad Google y desafíos temporales; no activa por sí misma el login Google |
| 0004 | Vista `perfil_estadisticas`: nombre, partidas jugadas, victorias y puntos |

## Relaciones

- `perfiles_jugador.usuario_id → usuarios.id`: PK compartida, relación uno a uno, ON DELETE CASCADE.
- `auth_tokens.user_id → usuarios.id`: varios tokens por cuenta, ON DELETE CASCADE.
- `cuentas_sociales.usuario_id → usuarios.id`: FK única, máximo una identidad Google por usuario, ON DELETE CASCADE.
- `participaciones.partida_id → partidas.id`: varias participaciones por partida, ON DELETE CASCADE.
- `participaciones.jugador_id → perfiles_jugador.usuario_id`: varias participaciones por jugador, ON DELETE RESTRICT.

Los IDs conservan el UUID textual del esquema original. Participación tiene PK `(partida_id, jugador_id)` y posición única por partida. Puntuaciones no negativas; posición positiva o NULL. Las fechas y el estado de la partida tienen restricciones de consistencia.

`records_jugador` agrega partidas FINALIZADA por jugador/modo/escenario. `perfil_estadisticas` reúne esos grupos para responder al perfil, con tres ceros cuando aún no hay resultados. Las vistas no duplican estadísticas mutables.

```sql
SELECT nombre_usuario, partidas_jugadas, partidas_ganadas, puntos_totales
FROM perfil_estadisticas
WHERE usuario_id = :usuario_id;
```

El parámetro enlazado de SQLAlchemy debe provenir del usuario autenticado por el backend, no de un ID arbitrario del cliente. Las victorias corresponden a posición 1; solo cuentan partidas finalizadas, entre todos los modos y escenarios. La respuesta no expone contraseñas, correo ni tokens.

## Responsabilidad de integración

El backend debe crear cuenta y perfil juntos, guardar hashes de contraseña y tokens, validar sesiones, consumir códigos una sola vez y revocar sesiones al recuperar contraseña. Las tablas soportan estos flujos; este cambio no implementa endpoints ni correo. La recuperación requiere código y contraseña nueva, no reenvío de la contraseña anterior.

El servidor del juego debe guardar participaciones/resultados y marcar FINALIZADA en una sola transacción. Borrar una partida elimina participaciones y cambia sus estadísticas; borrar un perfil con historial está restringido.

Modo y escenario siguen siendo texto. Referencias a catálogos, hardware, temporadas, reglas de empates y bajas deben acordarse con el equipo antes de una migración adicional. No se inventan entidades ajenas al modelo actual.

Consultar [la guía de aplicación](../sql/README.md) y [las pruebas](../testing/resultado-sql-moises.md).
