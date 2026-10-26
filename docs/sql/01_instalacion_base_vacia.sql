-- Entrega SQL Moises. Origen: base; destino: 0004.
-- Ejecutar SOLO el archivo correspondiente al estado actual, o usar Alembic.
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001

CREATE TABLE usuarios (
    id VARCHAR(36) NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_username UNIQUE (username),
    CONSTRAINT uq_usuarios_email UNIQUE (email)
);

INSERT INTO alembic_version (version_num) VALUES ('0001') RETURNING alembic_version.version_num;

-- Running upgrade 0001 -> 0002

CREATE UNIQUE INDEX uq_usuarios_email_lower ON usuarios (lower(email));

CREATE UNIQUE INDEX uq_usuarios_username_lower ON usuarios (lower(username));

CREATE TABLE auth_tokens (
    digest VARCHAR(64) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    purpose VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (digest),
    CONSTRAINT ck_token_purpose CHECK (purpose IN ('verify', 'reset', 'session')),
    FOREIGN KEY(user_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

CREATE INDEX ix_auth_tokens_user_purpose ON auth_tokens (user_id, purpose);

CREATE INDEX ix_auth_tokens_expires ON auth_tokens (expires_at);

CREATE TABLE perfiles_jugador (
    usuario_id VARCHAR(36) NOT NULL,
    nivel INTEGER DEFAULT '1' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (usuario_id),
    CONSTRAINT ck_perfil_nivel CHECK (nivel >= 1),
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

INSERT INTO perfiles_jugador (usuario_id) SELECT id FROM usuarios;

CREATE TABLE partidas (
    id VARCHAR(36) NOT NULL,
    escenario VARCHAR(100) NOT NULL,
    modo VARCHAR(50) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ESPERA' NOT NULL,
    limite_segundos INTEGER NOT NULL,
    puntuacion_objetivo INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    CONSTRAINT ck_partida_estado CHECK (estado IN ('ESPERA','EN_CURSO','FINALIZADA','CANCELADA')),
    CONSTRAINT ck_partida_limites CHECK (limite_segundos > 0 AND puntuacion_objetivo > 0),
    CONSTRAINT ck_partida_fechas CHECK (ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at)),
    CONSTRAINT ck_partida_finalizada CHECK (estado != 'FINALIZADA' OR ended_at IS NOT NULL),
    CONSTRAINT ck_partida_iniciada CHECK (estado != 'EN_CURSO' OR started_at IS NOT NULL)
);

CREATE TABLE participaciones (
    partida_id VARCHAR(36) NOT NULL,
    jugador_id VARCHAR(36) NOT NULL,
    puntuacion INTEGER DEFAULT '0' NOT NULL,
    posicion INTEGER,
    PRIMARY KEY (partida_id, jugador_id),
    CONSTRAINT ck_participacion_puntuacion CHECK (puntuacion >= 0),
    CONSTRAINT ck_participacion_posicion CHECK (posicion IS NULL OR posicion >= 1),
    CONSTRAINT uq_partida_posicion UNIQUE (partida_id, posicion),
    FOREIGN KEY(partida_id) REFERENCES partidas (id) ON DELETE CASCADE,
    FOREIGN KEY(jugador_id) REFERENCES perfiles_jugador (usuario_id) ON DELETE RESTRICT
);

CREATE INDEX ix_participaciones_jugador ON participaciones (jugador_id);

CREATE VIEW records_jugador AS
        SELECT p.jugador_id, m.modo, m.escenario,
               MAX(p.puntuacion) AS mejor_puntuacion,
               SUM(p.puntuacion) AS puntuacion_acumulada,
               COUNT(*) AS partidas_jugadas,
               SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) AS victorias
        FROM participaciones p JOIN partidas m ON m.id = p.partida_id
        WHERE m.estado = 'FINALIZADA'
        GROUP BY p.jugador_id, m.modo, m.escenario;

UPDATE alembic_version SET version_num='0002' WHERE alembic_version.version_num = '0001';

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
