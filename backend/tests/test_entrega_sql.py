"""Pruebas PostgreSQL en esquemas temporales dentro de transacciones revertidas.

SQL_TEST_DSN apunta a una base de pruebas; PGPASSWORD puede suministrar la clave.
No aplica migraciones al esquema public ni a reactor_moises_visualizacion.
"""
from io import StringIO
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest
from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[2]


def generated_upgrade(start, end):
    out = StringIO()
    cfg = Config(str(ROOT / 'backend/tools/sql_delivery/alembic.ini'), output_buffer=out)
    command.upgrade(cfg, f'{start}:{end}', sql=True)
    return out.getvalue()


def execute_migration(conn, source):
    # El fixture controla la transacción externa y siempre revierte todo.
    source = '\n'.join(line for line in source.splitlines() if line.strip() not in {'BEGIN;', 'COMMIT;'})
    conn.execute(source, prepare=False)


@pytest.fixture
def db():
    dsn = os.environ.get('SQL_TEST_DSN')
    if not dsn:
        pytest.skip('Configurar SQL_TEST_DSN para ejecutar contra PostgreSQL')
    conn = psycopg.connect(dsn)
    try:
        name = 'test_entrega_sql_' + uuid4().hex
        conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(name)))
        conn.execute(sql.SQL('SET LOCAL search_path TO {}').format(sql.Identifier(name)))
        yield conn
    finally:
        conn.rollback()  # Incluye la creación del esquema; no queda ningún objeto.
        conn.close()


def install(conn):
    execute_migration(conn, (ROOT / 'docs/sql/01_instalacion_base_vacia.sql').read_text(encoding='utf-8'))


def account(conn, user='player', profile=True):
    conn.execute("""INSERT INTO usuarios(id,username,email,password_hash,status)
                    VALUES (%s,%s,%s,'hash_ficticio_no_login','ACTIVA')""",
                 (user, user, user + '@example.invalid'))
    if profile:
        conn.execute('INSERT INTO perfiles_jugador(usuario_id) VALUES (%s)', (user,))


def stats(conn, user):
    return conn.execute("""SELECT nombre_usuario, partidas_jugadas, partidas_ganadas, puntos_totales
                           FROM perfil_estadisticas WHERE usuario_id=%s""", (user,)).fetchone()


def test_install_revision_relations_and_public_profile_columns(db):
    install(db)
    assert db.execute('SELECT version_num FROM alembic_version').fetchone() == ('0004',)
    assert db.execute("SELECT count(*) FROM pg_constraint WHERE contype='f' AND connamespace=current_schema()::regnamespace").fetchone()[0] == 5
    assert db.execute("SELECT count(*) FROM information_schema.views WHERE table_schema=current_schema()").fetchone()[0] == 2
    columns = db.execute("""SELECT column_name FROM information_schema.columns
                            WHERE table_schema=current_schema() AND table_name='perfil_estadisticas'
                            ORDER BY ordinal_position""").fetchall()
    assert [row[0] for row in columns] == ['usuario_id', 'nombre_usuario', 'partidas_jugadas', 'partidas_ganadas', 'puntos_totales']


def test_new_player_has_zero_totals(db):
    install(db)
    account(db)
    assert stats(db, 'player') == ('player', 0, 0, 0)
    assert stats(db, 'inexistente') is None


def test_totals_only_own_finished_matches_all_modes_and_scenarios(db):
    install(db)
    account(db)
    account(db, 'other')
    for user, state, score, position, mode, arena in [
        ('player', 'FINALIZADA', 100, 1, 'solo', 'A'),
        ('player', 'FINALIZADA', 40, 2, 'equipo', 'B'),
        ('player', 'FINALIZADA', 0, None, 'solo', 'A'),
        ('player', 'ESPERA', 900, None, 'solo', 'A'),
        ('player', 'EN_CURSO', 900, 1, 'solo', 'A'),
        ('player', 'CANCELADA', 900, 1, 'solo', 'A'),
        ('other', 'FINALIZADA', 800, 1, 'solo', 'A'),
    ]:
        match = str(uuid4())
        db.execute("""INSERT INTO partidas(id,escenario,modo,estado,limite_segundos,puntuacion_objetivo,started_at,ended_at)
                      VALUES (%s,%s,%s,%s,60,100,now(),CASE WHEN %s='FINALIZADA' THEN now() END)""",
                   (match, arena, mode, state, state))
        db.execute('INSERT INTO participaciones(partida_id,jugador_id,puntuacion,posicion) VALUES (%s,%s,%s,%s)',
                   (match, user, score, position))
    assert stats(db, 'player') == ('player', 3, 1, 140)
    assert stats(db, 'other') == ('other', 1, 1, 800)


@pytest.mark.parametrize('revision,filename', [
    ('0001', '02_actualizar_desde_0001.sql'),
    ('0002', '03_actualizar_desde_0002.sql'),
    ('0003', '04_actualizar_desde_0003.sql'),
])
def test_upgrade_preserves_existing_account_and_profile(db, revision, filename):
    execute_migration(db, generated_upgrade('base', revision))
    account(db, profile=revision != '0001')
    execute_migration(db, (ROOT / 'docs/sql' / filename).read_text(encoding='utf-8'))
    assert db.execute('SELECT version_num FROM alembic_version').fetchone() == ('0004',)
    assert db.execute('SELECT password_hash FROM usuarios').fetchone()[0] == 'hash_ficticio_no_login'
    assert stats(db, 'player') == ('player', 0, 0, 0)


def test_script_rejects_wrong_initial_revision_without_changes(db):
    install(db)
    account(db)
    with pytest.raises(psycopg.errors.RaiseException), db.transaction():
        execute_migration(db, (ROOT / 'docs/sql/02_actualizar_desde_0001.sql').read_text(encoding='utf-8'))
    assert db.execute('SELECT version_num FROM alembic_version').fetchone() == ('0004',)
    assert stats(db, 'player') == ('player', 0, 0, 0)


def test_profile_view_downgrade_keeps_tables_and_can_be_reapplied(db):
    install(db)
    account(db)
    out = StringIO()
    cfg = Config(str(ROOT / 'backend/tools/sql_delivery/alembic.ini'), output_buffer=out)
    command.downgrade(cfg, '0004:0003', sql=True)
    execute_migration(db, out.getvalue())
    assert db.execute("SELECT to_regclass('perfil_estadisticas')").fetchone()[0] is None
    assert db.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 1
    execute_migration(db, (ROOT / 'docs/sql/04_actualizar_desde_0003.sql').read_text(encoding='utf-8'))
    assert stats(db, 'player') == ('player', 0, 0, 0)


def test_duplicate_case_blocks_upgrade_preserving_accounts(db):
    execute_migration(db, generated_upgrade('base', '0001'))
    account(db, 'Player', profile=False)
    account(db, 'player', profile=False)
    with pytest.raises(psycopg.errors.UniqueViolation), db.transaction():
        execute_migration(db, (ROOT / 'docs/sql/02_actualizar_desde_0001.sql').read_text(encoding='utf-8'))
    assert db.execute('SELECT count(*) FROM usuarios').fetchone()[0] == 2
    assert db.execute('SELECT version_num FROM alembic_version').fetchone()[0] == '0001'
