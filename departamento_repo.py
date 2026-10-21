"""CRUD parametrizado de Departamento y asignación de empleados."""
import sqlite3

from dominio.departamento import Departamento
from dominio.excepciones import DepartamentoNoEncontradoError, ErrorPersistencia
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.errores_bd import traducir_error_sqlite


class DepartamentoRepositorio:
    def __init__(self, conexion: sqlite3.Connection):
        self._conn = conexion

    @staticmethod
    def _fila_a_departamento(fila: sqlite3.Row) -> Departamento:
        return Departamento(fila["nombre"], fila["gerente"], fila["id_departamento"])

    def guardar(self, departamento: Departamento) -> Departamento:
        try:
            cur = self._conn.execute(
                "INSERT INTO departamento (nombre, gerente) VALUES (?, ?)",
                (departamento.nombre, departamento.gerente))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        departamento.asignar_id(cur.lastrowid)
        return departamento

    def obtener_por_id(self, id_departamento: int) -> Departamento:
        try:
            fila = self._conn.execute(
                "SELECT id_departamento, nombre, gerente FROM departamento "
                "WHERE id_departamento = ?", (id_departamento,)).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        if fila is None:
            raise DepartamentoNoEncontradoError(
                f"No existe el departamento con ID {id_departamento}.")
        departamento = self._fila_a_departamento(fila)
        for empleado in EmpleadoRepositorio(self._conn).listar_por_departamento(id_departamento):
            departamento.agregar_empleado(empleado)
        return departamento

    def listar(self) -> list:
        try:
            filas = self._conn.execute(
                "SELECT id_departamento, nombre, gerente FROM departamento ORDER BY nombre"
            ).fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return [self._fila_a_departamento(f) for f in filas]

    def actualizar(self, departamento: Departamento) -> None:
        try:
            cur = self._conn.execute(
                "UPDATE departamento SET nombre = ?, gerente = ? WHERE id_departamento = ?",
                (departamento.nombre, departamento.gerente, departamento.id_departamento))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise DepartamentoNoEncontradoError("No existe el departamento a actualizar.")

    def eliminar(self, id_departamento: int) -> None:
        """Los empleados quedan sin departamento (ON DELETE SET NULL): agregación."""
        try:
            cur = self._conn.execute(
                "DELETE FROM departamento WHERE id_departamento = ?", (id_departamento,))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise DepartamentoNoEncontradoError("No existe el departamento a eliminar.")

    def agregar_empleado(self, departamento: Departamento, empleado) -> None:
        """Dominio primero (regla de negocio), luego persistencia; revierte si falla."""
        departamento.agregar_empleado(empleado)
        try:
            cur = self._conn.execute(
                "UPDATE empleado SET id_departamento = ? WHERE id_usuario = ? AND activo = 1",
                (departamento.id_departamento, empleado.id_usuario))
            self._conn.commit()
            if cur.rowcount == 0:
                raise ErrorPersistencia("El empleado no existe o está dado de baja.")
        except sqlite3.Error as error:
            self._conn.rollback()
            departamento.eliminar_empleado(empleado)
            raise traducir_error_sqlite(error) from error
        except ErrorPersistencia:
            departamento.eliminar_empleado(empleado)
            raise
