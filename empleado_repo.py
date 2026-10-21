"""CRUD parametrizado de Empleado y mapper fila -> objeto."""
import sqlite3
from datetime import date

from dominio.empleado import Empleado
from dominio.excepciones import EmpleadoNoEncontradoError
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from repositorio.errores_bd import traducir_error_sqlite


class EmpleadoRepositorio:
    def __init__(self, conexion: sqlite3.Connection):
        self._conn = conexion

    # --- mapper único: toda fila se convierte en Empleado aquí -------------
    @staticmethod
    def _fila_a_empleado(fila: sqlite3.Row) -> Empleado:
        return Empleado(
            nombre_usuario=fila["nombre_usuario"], password_hash=fila["password_hash"],
            nombre=fila["nombre"], direccion=fila["direccion"], telefono=fila["telefono"],
            email=fila["email"],
            fecha_inicio_contrato=date.fromisoformat(fila["fecha_inicio_contrato"]),
            salario=fila["salario"], id_usuario=fila["id_usuario"])

    # --- Create (transacción atómica de dos escrituras) ---------------------
    def guardar(self, empleado: Empleado) -> Empleado:
        try:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO usuario (nombre_usuario, password_hash, rol) VALUES (?, ?, ?)",
                (empleado.nombre_usuario, empleado.password_hash, empleado.rol))
            empleado.asignar_id(cur.lastrowid)
            cur.execute(
                "INSERT INTO empleado (id_usuario, nombre, direccion, telefono, email, "
                "fecha_inicio_contrato, salario) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (empleado.id_usuario, empleado.nombre, empleado.direccion,
                 empleado.telefono, empleado.email,
                 empleado.fecha_inicio_contrato.isoformat(), empleado.salario))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            empleado.asignar_id(None)
            raise traducir_error_sqlite(error) from error
        return empleado

    # --- Read ----------------------------------------------------------------
    def obtener_por_id(self, id_usuario: int) -> Empleado:
        try:
            fila = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, e.nombre, e.direccion, "
                "e.telefono, e.email, e.fecha_inicio_contrato, e.salario "
                "FROM empleado e JOIN usuario u ON u.id_usuario = e.id_usuario "
                "WHERE e.id_usuario = ? AND e.activo = 1",
                (id_usuario,)).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        if fila is None:
            raise EmpleadoNoEncontradoError(f"No existe el empleado con ID {id_usuario}.")
        return self._fila_a_empleado(fila)

    def buscar_por_email(self, email: str):
        """Devuelve el Empleado o None; el email viaja como parámetro, no como SQL."""
        try:
            fila = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, e.nombre, e.direccion, "
                "e.telefono, e.email, e.fecha_inicio_contrato, e.salario "
                "FROM empleado e JOIN usuario u ON u.id_usuario = e.id_usuario "
                "WHERE e.email = ? AND e.activo = 1", (email,)
            ).fetchone()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return self._fila_a_empleado(fila) if fila else None

    def listar_activos(self) -> list:
        try:
            filas = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, e.nombre, e.direccion, "
                "e.telefono, e.email, e.fecha_inicio_contrato, e.salario "
                "FROM empleado e JOIN usuario u ON u.id_usuario = e.id_usuario "
                "WHERE e.activo = 1 ORDER BY e.nombre").fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return [self._fila_a_empleado(f) for f in filas]

    def listar_por_departamento(self, id_departamento: int) -> list:
        try:
            filas = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, e.nombre, e.direccion, "
                "e.telefono, e.email, e.fecha_inicio_contrato, e.salario "
                "FROM empleado e JOIN usuario u ON u.id_usuario = e.id_usuario "
                "WHERE e.id_departamento = ? AND e.activo = 1 "
                "ORDER BY e.nombre", (id_departamento,)).fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return [self._fila_a_empleado(f) for f in filas]

    def listar_por_proyecto(self, id_proyecto: int) -> list:
        try:
            filas = self._conn.execute(
                "SELECT u.id_usuario, u.nombre_usuario, u.password_hash, e.nombre, e.direccion, "
                "e.telefono, e.email, e.fecha_inicio_contrato, e.salario "
                "FROM empleado e JOIN usuario u ON u.id_usuario = e.id_usuario "
                "JOIN empleado_proyecto ep ON ep.id_usuario = e.id_usuario "
                "WHERE ep.id_proyecto = ? AND e.activo = 1 ORDER BY e.nombre",
                (id_proyecto,)).fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        return [self._fila_a_empleado(f) for f in filas]

    def cargar_registros(self, empleado: Empleado) -> Empleado:
        """Hidrata la composición Empleado -> RegistroTiempo."""
        try:
            filas = self._conn.execute(
                "SELECT r.id_registro, r.fecha, r.horas, r.descripcion, "
                "p.id_proyecto, p.nombre, p.descripcion AS desc_proyecto, p.fecha_inicio "
                "FROM registro_tiempo r JOIN proyecto p ON p.id_proyecto = r.id_proyecto "
                "WHERE r.id_usuario = ? ORDER BY r.fecha, r.id_registro",
                (empleado.id_usuario,)).fetchall()
        except sqlite3.Error as error:
            raise traducir_error_sqlite(error) from error
        registros = []
        for f in filas:
            proyecto = Proyecto(f["nombre"], f["desc_proyecto"],
                                date.fromisoformat(f["fecha_inicio"]), f["id_proyecto"])
            registros.append(RegistroTiempo(
                date.fromisoformat(f["fecha"]), f["horas"], f["descripcion"], proyecto,
                id_usuario=empleado.id_usuario, id_registro=f["id_registro"]))
        empleado.cargar_registros(registros)
        return empleado

    # --- Update ----------------------------------------------------------------
    def actualizar(self, empleado: Empleado) -> None:
        try:
            cur = self._conn.execute(
                "UPDATE empleado SET nombre = ?, direccion = ?, telefono = ?, email = ?, "
                "salario = ? WHERE id_usuario = ? AND activo = 1",
                (empleado.nombre, empleado.direccion, empleado.telefono, empleado.email,
                 empleado.salario, empleado.id_usuario))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise EmpleadoNoEncontradoError("No existe el empleado a actualizar.")

    # --- Delete (borrado lógico: conserva el historial de horas) ----------------
    def eliminar(self, id_usuario: int) -> None:
        try:
            cur = self._conn.execute(
                "UPDATE empleado SET activo = 0, id_departamento = NULL "
                "WHERE id_usuario = ? AND activo = 1", (id_usuario,))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        if cur.rowcount == 0:
            raise EmpleadoNoEncontradoError("No existe el empleado a dar de baja.")

    # --- Asignaciones -------------------------------------------------------------
    def asignar_a_proyecto(self, id_usuario: int, id_proyecto: int) -> None:
        try:
            self._conn.execute(
                "INSERT INTO empleado_proyecto (id_usuario, id_proyecto) VALUES (?, ?)",
                (id_usuario, id_proyecto))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error

    def desasignar_de_proyecto(self, id_usuario: int, id_proyecto: int) -> bool:
        try:
            cur = self._conn.execute(
                "DELETE FROM empleado_proyecto WHERE id_usuario = ? AND id_proyecto = ?",
                (id_usuario, id_proyecto))
            self._conn.commit()
        except sqlite3.Error as error:
            self._conn.rollback()
            raise traducir_error_sqlite(error) from error
        return cur.rowcount > 0
