"""Exporta SQL sin conectarse a PostgreSQL; exige revisión inicial exacta."""
from io import StringIO
from pathlib import Path
from alembic import command
from alembic.config import Config

root = Path(__file__).resolve().parents[3]
(root / 'docs/sql').mkdir(exist_ok=True)
for revision, filename in [
    ('base', '01_instalacion_base_vacia.sql'),
    ('0001', '02_actualizar_desde_0001.sql'),
    ('0002', '03_actualizar_desde_0002.sql'),
    ('0003', '04_actualizar_desde_0003.sql'),
]:
    output = StringIO()
    config = Config(str(root / 'backend/tools/sql_delivery/alembic.ini'), output_buffer=output)
    command.upgrade(config, f'{revision}:0004', sql=True)
    sql = output.getvalue()
    if revision != 'base':
        guard = f"""DO $revision_guard$
BEGIN
    IF (SELECT count(*) FROM alembic_version) <> 1
       OR NOT EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '{revision}') THEN
        RAISE EXCEPTION 'Este archivo requiere revision {revision}; no se aplicaron cambios';
    END IF;
END
$revision_guard$;

"""
        sql = sql.replace('BEGIN;\n', 'BEGIN;\n\n' + guard, 1)
    header = f'-- Entrega SQL Moises. Origen: {revision}; destino: 0004.\n'
    header += '-- Ejecutar SOLO el archivo correspondiente al estado actual, o usar Alembic.\n'
    sql = '\n'.join(line.rstrip() for line in (header + sql).splitlines()).rstrip() + '\n'
    (root / 'docs/sql' / filename).write_text(sql, encoding='utf-8')
    print(filename)
