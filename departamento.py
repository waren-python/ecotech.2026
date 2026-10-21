"""Departamento agrupa empleados (agregación 1 — 0..*)."""
from dominio.excepciones import AsignacionInvalidaError, DatoInvalidoError


class Departamento:
    def __init__(self, nombre: str, gerente: str, id_departamento: int | None = None):
        self._id_departamento = id_departamento
        self._nombre = ""
        self._gerente = ""
        self.nombre = nombre
        self.gerente = gerente
        self._empleados: list = []   # los empleados existen fuera del departamento

    @property
    def id_departamento(self):
        return self._id_departamento

    def asignar_id(self, valor) -> None:
        self._id_departamento = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not 2 <= len(valor.strip()) <= 100:
            raise DatoInvalidoError("El nombre del departamento debe tener 2 a 100 caracteres.")
        self._nombre = valor.strip()

    @property
    def gerente(self) -> str:
        return self._gerente

    @gerente.setter
    def gerente(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El nombre del gerente es obligatorio.")
        self._gerente = valor.strip()

    @property
    def empleados(self) -> tuple:
        return tuple(self._empleados)

    def agregar_empleado(self, empleado) -> None:
        if empleado in self._empleados:
            raise AsignacionInvalidaError(
                f"{empleado.nombre} ya pertenece al departamento {self.nombre}.")
        self._empleados.append(empleado)

    def eliminar_empleado(self, empleado) -> bool:
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            return True
        return False
