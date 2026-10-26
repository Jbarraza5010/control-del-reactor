# Aplicación de las migraciones SQL

La base de destino debe existir; esta entrega no contiene credenciales ni configuración de un servidor específico. Las migraciones conservan `0001` y añaden `0002 → 0003 → 0004`.

## Alembic (ruta preferida)

Con el entorno Python del backend activo y DATABASE_URL configurada para el servidor del equipo, desde `backend`:

```powershell
python -m alembic current
python -m alembic heads
# Revisar revisión y cabezas antes de aplicar. La cabeza esperada es 0004.
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

Confirmar que otras ramas no hayan usado estos números de revisión para migraciones diferentes. Las vistas se gestionan por migración, no por autogenerate; verificarlas con `06_verificar_estructura.sql`. Con datos existentes, obtener respaldo antes de aplicar. Si hay tablas sin historial Alembic, reconciliar primero el esquema; no usar stamp para omitir esa revisión.

## SQL directo (alternativa)

Elegir un único archivo según el estado real. No ejecutar todos ni aplicar una segunda actualización equivalente por Alembic.

| Estado | Archivo |
|---|---|
| Esquema vacío | 01_instalacion_base_vacia.sql |
| Revisión 0001 | 02_actualizar_desde_0001.sql |
| Revisión 0002 | 03_actualizar_desde_0002.sql |
| Revisión 0003 | 04_actualizar_desde_0003.sql |
| Revisión 0004 | Solo verificar |

Los scripts tienen transacción y registran la revisión final. Los de actualización rechazan una revisión inicial incorrecta. Duplicados de usuario/correo por mayúsculas detienen la creación de índices sin borrar ni fusionar cuentas: el equipo debe resolverlos primero.

Desde la raíz del repositorio, reemplazar los marcadores por los datos del administrador. Este ejemplo de actualización es válido únicamente para revisión 0001:

```powershell
psql -h HOST_EQUIPO -U USUARIO_EQUIPO -d BASE_EQUIPO -W -c "SELECT current_database(), current_schema(), to_regclass('alembic_version');"
# Si existe alembic_version:
psql -h HOST_EQUIPO -U USUARIO_EQUIPO -d BASE_EQUIPO -W -c "SELECT version_num FROM alembic_version;"
psql -h HOST_EQUIPO -U USUARIO_EQUIPO -d BASE_EQUIPO -W -v ON_ERROR_STOP=1 -f docs/sql/02_actualizar_desde_0001.sql
psql -h HOST_EQUIPO -U USUARIO_EQUIPO -d BASE_EQUIPO -W -v ON_ERROR_STOP=1 -f docs/sql/06_verificar_estructura.sql
```

Confirmar esquema, puerto y TLS según el servidor. En pgAdmin se puede abrir el archivo elegido y ejecutarlo completo sobre la base/esquema correctos. `05_consultar_perfil.sql` es una lectura para psql que requiere `-v usuario_id=UUID_AUTENTICADO`; el backend debe validar la sesión antes de obtener ese ID.

## Regenerar SQL y ejecutar pruebas

Con las dependencias de desarrollo del backend instaladas, desde la raíz:

```powershell
python backend/tools/sql_delivery/generar_sql.py
# Configurar SQL_TEST_DSN hacia PostgreSQL de pruebas y credenciales en el proceso.
python -m pytest backend/tests/test_entrega_sql.py -q
```

`SQL_TEST_DSN` acepta URI PostgreSQL de psycopg (sin `+psycopg`). No guardar contraseñas en Git. Cada prueba crea un esquema dentro de una transacción y revierte todo, incluido el esquema; requiere permiso CREATE SCHEMA. Sin SQL_TEST_DSN estas pruebas se omiten, lo que no constituye validación PostgreSQL.

El entorno `backend/tools/sql_delivery/alembic/` sirve solo para exportación y pruebas. No reemplaza `backend/alembic/env.py`. Los SQL se generan desde las mismas migraciones para evitar dos definiciones divergentes del modelo.
