"""Conexión oficial (sqlite3) y lectura segura de variables de entorno."""
import contextlib
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from dominio.excepciones import ConexionBDError

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")        # el .env real nunca se versiona


def ruta_bd() -> Path:
    ruta = Path(os.getenv("ECOTECH_DB_PATH", "datos/ecotech.db"))
    return ruta if ruta.is_absolute() else RAIZ / ruta


def conectar(ruta=None) -> sqlite3.Connection:
    try:
        conexion = sqlite3.connect(str(ruta or ruta_bd()))
        conexion.row_factory = sqlite3.Row
        # SQLite NO aplica llaves foráneas por defecto: se activa en cada conexión.
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion
    except sqlite3.Error as error:
        raise ConexionBDError("No fue posible abrir la base de datos.") from error


def inicializar_bd(ruta=None) -> None:
    try:
        script = (RAIZ / "datos" / "schema.sql").read_text(encoding="utf-8")
        with contextlib.closing(conectar(ruta)) as conexion:
            conexion.executescript(script)
    except (OSError, sqlite3.Error) as error:
        raise ConexionBDError("No fue posible inicializar el esquema.") from error
