"""Proyecto: iniciativa con empleados asignados (asociación 0..* — 0..*)."""
from datetime import date

from dominio.excepciones import AsignacionInvalidaError, DatoInvalidoError, FechaInvalidaError


class Proyecto:
    def __init__(self, nombre: str, descripcion: str, fecha_inicio: date,
                 id_proyecto: int | None = None):
        self._id_proyecto = id_proyecto
        self._nombre = ""
        self._descripcion = ""
        self._fecha_inicio = None
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self._empleados: list = []

    @property
    def id_proyecto(self):
        return self._id_proyecto

    def asignar_id(self, valor) -> None:
        self._id_proyecto = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not 2 <= len(valor.strip()) <= 100:
            raise DatoInvalidoError("El nombre del proyecto debe tener 2 a 100 caracteres.")
        self._nombre = valor.strip()

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("La descripción del proyecto es obligatoria.")
        self._descripcion = valor.strip()

    @property
    def fecha_inicio(self) -> date:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor: date) -> None:
        if not isinstance(valor, date) or valor.year < 1950:
            raise FechaInvalidaError("La fecha de inicio del proyecto no es válida.")
        self._fecha_inicio = valor

    @property
    def empleados(self) -> tuple:
        return tuple(self._empleados)

    def asignar_empleado(self, empleado) -> None:
        if empleado in self._empleados:
            raise AsignacionInvalidaError(
                f"{empleado.nombre} ya está asignado al proyecto {self.nombre}.")
        self._empleados.append(empleado)

    def desasignar_empleado(self, empleado) -> bool:
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            return True
        return False
