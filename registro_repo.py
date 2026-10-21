"""Persistencia de RegistroTiempo."""
import sqlite3

from dominio.excepciones import AsignacionInvalidaError, ErrorPersistencia
from dominio.registro_tiempo import RegistroTiempo
from repositorio.errores_bd import traducir_error_sqlite


class RegistroRepositorio:
    def __init__(self, conexion: sqlite3.Connection):
        self._conn = conexion

    def guardar(self, registro: RegistroTiempo) -> None:
        try:
            self._conn.execute(
                "INSERT INTO registro_tiempo (id_usuario, id_proyecto, fecha, horas, descripcion) "
                "VALUES (?, ?, ?, ?, ?)",
                (registro.id_usuario, registro.proyecto.id_proyecto,
                 registro.fecha.isoformat(), registro.horas_trabajadas,
                 registro.descripcion_tarea))
            self._conn.commit()
        except sqlite3.IntegrityError as error:
            self._conn.rollback()
            if "FOREIGN KEY" in str(error):
                raise AsignacionInvalidaError(
                    "El empleado no está asignado a ese proyecto.") from error
            raise traducir_error_sqlite(error) from error
        except sqlite3.Error as error:
            self._conn.rollback()
            raise ErrorPersistencia("No se pudo guardar el registro de horas.") from error
