"""CRUD parametrizado de Proyecto."""
import sqlite3
from datetime import date

from dominio.excepciones import ProyectoNoEncontradoError
from dominio.proyecto import Proyecto
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.errores_bd import traducir_error_sqlite


class ProyectoRepositorio:
    def __init__(self, conexion: sqlite3.Connection):
        self._conn = conexion

    @staticmethod
    def _fila_a_proyecto(fila: sqlite3.Row) -> Proyecto:
        return Proyecto(fila["nombre"], fila["descripcion"],
                        date.fromisoformat(fila["fecha_inicio"]), fila["id_proyecto"])

    def guardar(self, proyecto: Proyecto) -> Proyecto:
        try:
            cur = self._conn.execute(
                "INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES (?, ?, ?)",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio.isoformat()))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        proyecto.asignar_id(cur.lastrowid)
        return proyecto

    def obtener_por_id(self, id_proyecto: int) -> Proyecto:
        try:
            fila = self._conn.execute(
                "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto "
                "WHERE id_proyecto = ?", (id_proyecto,)).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        if fila is None:
            raise ProyectoNoEncontradoError(f"No existe el proyecto con ID {id_proyecto}.")
        proyecto = self._fila_a_proyecto(fila)
        for empleado in EmpleadoRepositorio(self._conn).listar_por_proyecto(id_proyecto):
            proyecto.asignar_empleado(empleado)
        return proyecto

    def listar(self) -> list:
        try:
            filas = self._conn.execute(
                "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto "
                "ORDER BY nombre").fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return [self._fila_a_proyecto(f) for f in filas]

    def actualizar(self, proyecto: Proyecto) -> None:
        try:
            cur = self._conn.execute(
                "UPDATE proyecto SET nombre = ?, descripcion = ?, fecha_inicio = ? "
                "WHERE id_proyecto = ?",
                (proyecto.nombre, proyecto.descripcion,
                 proyecto.fecha_inicio.isoformat(), proyecto.id_proyecto))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise ProyectoNoEncontradoError("No existe el proyecto a actualizar.")

    def eliminar(self, id_proyecto: int) -> None:
        """Falla si el proyecto ya tiene horas registradas (FK sin cascada)."""
        try:
            cur = self._conn.execute(
                "DELETE FROM proyecto WHERE id_proyecto = ?", (id_proyecto,))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise ProyectoNoEncontradoError("No existe el proyecto a eliminar.")
