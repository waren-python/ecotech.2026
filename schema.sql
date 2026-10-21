-- Esquema relacional EcoTech (SQLite 3). Se ejecuta con inicializar_bd().
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departamento (
    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL UNIQUE,
    gerente         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    rol            TEXT NOT NULL CHECK (rol IN ('EMPLEADO', 'ADMINISTRADOR'))
);

CREATE TABLE IF NOT EXISTS administrador (
    id_usuario       INTEGER PRIMARY KEY,
    area_responsable TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS empleado (
    id_usuario            INTEGER PRIMARY KEY,
    nombre                TEXT NOT NULL,
    direccion             TEXT NOT NULL,
    telefono              TEXT NOT NULL,
    email                 TEXT NOT NULL UNIQUE,
    fecha_inicio_contrato TEXT NOT NULL,
    salario               REAL NOT NULL CHECK (salario > 0),
    activo                INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    id_departamento       INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_departamento) REFERENCES departamento (id_departamento)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS proyecto (
    id_proyecto  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL UNIQUE,
    descripcion  TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleado_proyecto (
    id_usuario  INTEGER NOT NULL,
    id_proyecto INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_proyecto),
    FOREIGN KEY (id_usuario) REFERENCES empleado (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_proyecto) REFERENCES proyecto (id_proyecto) ON DELETE CASCADE
);

-- Composición Empleado 1 — 0..* RegistroTiempo; la FK compuesta obliga a que
-- el empleado esté asignado al proyecto en el que registra horas.
CREATE TABLE IF NOT EXISTS registro_tiempo (
    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario  INTEGER NOT NULL,
    id_proyecto INTEGER NOT NULL,
    fecha       TEXT NOT NULL,
    horas       REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
    descripcion TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES empleado (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario, id_proyecto)
        REFERENCES empleado_proyecto (id_usuario, id_proyecto)
);
