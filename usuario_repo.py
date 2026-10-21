"""Repositorio de Usuario: autenticación y mapeo polimórfico por rol."""
import sqlite3
from datetime import date

from dominio.administrador import Administrador
from dominio.empleado import Empleado
from dominio.excepciones import CredencialesInvalidasError
from dominio.seguridad import verificar_password
from repositorio.errores_bd import traducir_error_sqlite

# Hash ficticio para igualar el tiempo de respuesta cuando el usuario no existe
_HASH_FICTICIO = "pbkdf2_sha256$200000$" + "00" * 16 + "$" + "00" * 32


class UsuarioRepositorio:
    def __init__(self, conexion: sqlite3.Connection):
        self._conn = conexion

    def autenticar(self, nombre_usuario: str, password: str):
        try:
            fila = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, u.rol, "
                "e.nombre, e.direccion, e.telefono, e.email, "
                "e.fecha_inicio_contrato, e.salario, a.area_responsable "
                "FROM usuario u "
                "LEFT JOIN empleado e ON e.id_usuario = u.id_usuario "
                "LEFT JOIN administrador a ON a.id_usuario = u.id_usuario "
                "WHERE u.nombre_usuario = ? AND COALESCE(e.activo, 1) = 1",
                (nombre_usuario,),
            ).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        almacenado = fila["password_hash"] if fila else _HASH_FICTICIO
        if not verificar_password(password, almacenado) or fila is None:
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")
        return self._fila_a_usuario(fila)

    def existe_administrador(self) -> bool:
        try:
            fila = self._conn.execute(
                "SELECT 1 FROM usuario WHERE rol = ? LIMIT 1", ("ADMINISTRADOR",)
            ).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return fila is not None

    def guardar_administrador(self, admin: Administrador) -> Administrador:
        """Transacción atómica: usuario + administrador, o ninguno."""
        try:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO usuario (nombre_usuario, password_hash, rol) VALUES (?, ?, ?)",
                (admin.nombre_usuario, admin.password_hash, admin.rol))
            admin.asignar_id(cur.lastrowid)
            cur.execute(
                "INSERT INTO administrador (id_usuario, area_responsable) VALUES (?, ?)",
                (admin.id_usuario, admin.area_responsable))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            admin.asignar_id(None)
            raise traducir_error_sqlite(error) from error
        return admin

    # --- mapeo centralizado fila -> objeto (sin isinstance: tabla por rol) ---
    @staticmethod
    def _fila_a_empleado(fila: sqlite3.Row) -> Empleado:
        return Empleado(
            fila["nombre_usuario"], fila["password_hash"], fila["nombre"],
            fila["direccion"], fila["telefono"], fila["email"],
            date.fromisoformat(fila["fecha_inicio_contrato"]), fila["salario"],
            id_usuario=fila["id_usuario"])

    @staticmethod
    def _fila_a_administrador(fila: sqlite3.Row) -> Administrador:
        return Administrador(fila["nombre_usuario"], fila["password_hash"],
                             fila["area_responsable"], id_usuario=fila["id_usuario"])

    @classmethod
    def _fila_a_usuario(cls, fila: sqlite3.Row):
        constructores = {"EMPLEADO": cls._fila_a_empleado,
                         "ADMINISTRADOR": cls._fila_a_administrador}
        return constructores[fila["rol"]](fila)
