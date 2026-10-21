"""RegistroTiempo: horas de un empleado en un proyecto (composición)."""
from datetime import date

from dominio.excepciones import FechaInvalidaError, HorasInvalidasError, NombreInvalidoError


class RegistroTiempo:
    HORAS_MAXIMAS_DIA = 24.0

    def __init__(self, fecha: date, horas_trabajadas: float,
                 descripcion_tarea: str, proyecto,
                 id_usuario: int | None = None, id_registro: int | None = None):
        self._fecha = None
        self._horas_trabajadas = 0.0
        self._descripcion_tarea = ""
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion_tarea = descripcion_tarea
        self._proyecto = proyecto            # RegistroTiempo 0..* — 1 Proyecto
        self._id_usuario = id_usuario        # dueño (composición)
        self._id_registro = id_registro
        self.validar()

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise FechaInvalidaError("La fecha del registro es obligatoria.")
        if valor > date.today():
            raise FechaInvalidaError("No se pueden registrar horas en el futuro.")
        self._fecha = valor

    @property
    def horas_trabajadas(self) -> float:
        return self._horas_trabajadas

    @horas_trabajadas.setter
    def horas_trabajadas(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise HorasInvalidasError("Las horas deben ser un número.")
        if not 0 < valor <= self.HORAS_MAXIMAS_DIA:
            raise HorasInvalidasError("Las horas deben estar entre 0 (exclusivo) y 24.")
        self._horas_trabajadas = float(valor)

    @property
    def descripcion_tarea(self) -> str:
        return self._descripcion_tarea

    @descripcion_tarea.setter
    def descripcion_tarea(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise NombreInvalidoError("La descripción de la tarea es obligatoria.")
        self._descripcion_tarea = valor.strip()

    @property
    def proyecto(self):
        return self._proyecto

    @property
    def id_usuario(self):
        return self._id_usuario

    @property
    def id_registro(self):
        return self._id_registro

    def validar(self) -> bool:
        """Verifica la coherencia del registro antes de guardarse."""
        self.fecha = self._fecha
        self.horas_trabajadas = self._horas_trabajadas
        self.descripcion_tarea = self._descripcion_tarea
        if self._proyecto is None:
            raise HorasInvalidasError("Cada registro debe pertenecer a un proyecto.")
        return True

    def __str__(self) -> str:
        return (f"{self.fecha.isoformat()} | {self.horas_trabajadas:g} h | "
                f"{self.proyecto.nombre} | {self.descripcion_tarea}")
