-- Solo lectura; ejecutar después de la instalación/actualización elegida.
SELECT version_num FROM alembic_version;

SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = current_schema()
ORDER BY table_name;

SELECT conrelid::regclass AS tabla, conname, pg_get_constraintdef(oid) AS referencia
FROM pg_constraint
WHERE contype = 'f' AND connamespace = current_schema()::regnamespace
ORDER BY conrelid::regclass::text, conname;
