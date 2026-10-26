-- Entrega SQL Moises. Origen: 0002; destino: 0004.
-- Ejecutar SOLO el archivo correspondiente al estado actual, o usar Alembic.
BEGIN;

DO $revision_guard$
BEGIN
    IF (SELECT count(*) FROM alembic_version) <> 1
       OR NOT EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '0002') THEN
        RAISE EXCEPTION 'Este archivo requiere revision 0002; no se aplicaron cambios';
    END IF;
END
$revision_guard$;


-- Running upgrade 0002 -> 0003

CREATE TABLE google_challenges (
    digest VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (digest)
);

CREATE TABLE cuentas_sociales (
    google_subject VARCHAR(255) NOT NULL,
    usuario_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (google_subject),
    CONSTRAINT uq_cuenta_social_usuario UNIQUE (usuario_id),
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

UPDATE alembic_version SET version_num='0003' WHERE alembic_version.version_num = '0002';

-- Running upgrade 0003 -> 0004

CREATE VIEW perfil_estadisticas AS
        SELECT u.id AS usuario_id,
               u.username AS nombre_usuario,
               CAST(COALESCE(SUM(r.partidas_jugadas), 0) AS BIGINT) AS partidas_jugadas,
               CAST(COALESCE(SUM(r.victorias), 0) AS BIGINT) AS partidas_ganadas,
               CAST(COALESCE(SUM(r.puntuacion_acumulada), 0) AS BIGINT) AS puntos_totales
        FROM usuarios u
        JOIN perfiles_jugador j ON j.usuario_id = u.id
        LEFT JOIN records_jugador r ON r.jugador_id = j.usuario_id
        GROUP BY u.id, u.username;

UPDATE alembic_version SET version_num='0004' WHERE alembic_version.version_num = '0003';

COMMIT;
