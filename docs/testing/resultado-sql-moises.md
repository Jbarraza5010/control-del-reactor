# Verificación del modelo SQL

24 de octubre de 2026. Base de integración: develop `d1b3313ceb471686243d10022bd4bfd18bbf0d67`.

**35 pruebas aprobadas, 0 fallos y 0 omitidas**, ejecutadas desde `backend` con `python -m pytest -q` y SQL_TEST_DSN configurada para PostgreSQL de pruebas. Incluyen la suite original del backend y 9 casos nuevos de entrega SQL. Evidencia: `resultado-sql-publicacion.xml`.

Las pruebas PostgreSQL crean esquemas aislados dentro de transacciones y revierten todo al finalizar. No se aplicaron migraciones a bases del equipo ni a la base local de visualización.

Cobertura SQL nueva:

- Instalación completa hasta 0004, dos vistas y cinco claves foráneas.
- Perfil sin resultados con ceros e ID inexistente sin fila.
- Estadísticas entre modos/escenarios; exclusión de partidas no finalizadas y resultados de otros jugadores.
- Actualización desde 0001, 0002 y 0003 conservando cuentas y hashes.
- Rechazo de un script para una revisión inicial distinta.
- Reversión de 0004 y reaplicación sin pérdida de cuentas o tablas.
- Duplicados por capitalización: rechazo controlado que conserva cuentas y revisión.

La vista de perfil utiliza CAST estándar, compatible con PostgreSQL y con la prueba SQLite de upgrade/downgrade del repositorio. Se mantienen las pruebas existentes sin omitirlas ni cambiar sus expectativas.

Advertencias existentes: deprecación de TestClient/httpx y de la configuración Alembic sin path_separator. No causan fallos. No se prueban Godot, SMTP, Google real ni un servidor del equipo: este cambio entrega exclusivamente estructura SQL, modelos y documentación.
