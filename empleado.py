"""Empleado: especialización de Usuario con datos personales y horas."""
import re
from datetime import date

from dominio.excepciones import (DatoInvalidoError, EmailInvalidoError, FechaInvalidaError,
                                 NombreInvalidoError, SalarioInvalidoError,
                                 TelefonoInvalidoError)
from dominio.registro_tiempo import RegistroTiempo
from dominio.usuario import Usuario

_PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PATRON_TELEFONO = re.compile(r"^\+?\d{8,12}$")


class Empleado(Usuario):
    ROL = "EMPLEADO"
    SALARIO_MAXIMO = 100_000_000.0
    CAMPOS_EDITABLES = ("nombre", "direccion", "telefono", "email")

    def __init__(self, nombre_usuario: str, password_hash: str, nombre: str,
                 direccion: str, telefono: str, email: str,
                 fecha_inicio_contrato: date, salario: float,
                 id_usuario: int | None = None):
        super().__init__(nombre_usuario, password_hash, id_usuario)
        self._nombre = ""
        self._direccion = ""
        self._telefono = ""
        self._email = ""
        self._fecha_inicio_contrato = None
        self._salario = 0.0
        self._registros: list[RegistroTiempo] = []   # composición
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self.salario = salario

    # --- atributos protegidos con validación -------------------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not 2 <= len(valor.strip()) <= 100:
            raise NombreInvalidoError("El nombre debe tener entre 2 y 100 caracteres.")
        self._nombre = valor.strip()

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("La dirección es obligatoria.")
        self._direccion = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = re.sub(r"[\s-]", "", valor) if isinstance(valor, str) else ""
        if not _PATRON_TELEFONO.match(limpio):
            raise TelefonoInvalidoError("El teléfono debe tener entre 8 y 12 dígitos.")
        self._telefono = limpio

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not isinstance(valor, str) or not _PATRON_EMAIL.match(valor.strip()):
            raise EmailInvalidoError("El correo electrónico no es válido.")
        self._email = valor.strip().lower()

    @property
    def fecha_inicio_contrato(self) -> date:
        return self._fecha_inicio_contrato

    @fecha_inicio_contrato.setter
    def fecha_inicio_contrato(self, valor: date) -> None:
        if not isinstance(valor, date) or valor > date.today() or valor.year < 1950:
            raise FechaInvalidaError("La fecha de contrato no es válida.")
        self._fecha_inicio_contrato = valor

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) \
                or not 0 < valor <= self.SALARIO_MAXIMO:
            raise SalarioInvalidoError("El salario debe ser mayor a 0 y menor al tope permitido.")
        self._salario = float(valor)

    @property
    def registros(self) -> tuple:
        return tuple(self._registros)

    # --- comportamiento del UML ---------------------------------------------
    def registrar_horas(self, fecha: date, horas: float, descripcion: str,
                        proyecto) -> RegistroTiempo:
        """El empleado es dueño del registro: él lo crea (composición)."""
        registro = RegistroTiempo(fecha, horas, descripcion, proyecto,
                                  id_usuario=self.id_usuario)
        self._registros.append(registro)
        return registro

    def cargar_registros(self, registros) -> None:
        """Hidratación desde la capa de datos (registros ya validados)."""
        self._registros = list(registros)

    def total_horas(self) -> float:
        return sum(r.horas_trabajadas for r in self._registros)

    def actualizar_datos(self, datos: dict) -> None:
        """Actualiza sólo los campos editables; es 'todo o nada' en memoria."""
        desconocidos = set(datos) - set(self.CAMPOS_EDITABLES)
        if desconocidos:
            raise DatoInvalidoError(
                f"Campos no editables: {', '.join(sorted(desconocidos))}.")
        respaldo = {campo: getattr(self, campo) for campo in datos}
        try:
            for campo, valor in datos.items():
                setattr(self, campo, valor)
        except DatoInvalidoError:
            for campo, valor in respaldo.items():
                setattr(self, campo, valor)
            raise

    # --- polimorfismo --------------------------------------------------------
    def modulos_permitidos(self) -> frozenset:
        return frozenset({"perfil", "horas", "proyectos"})

    def descripcion(self) -> str:
        return f"{self.nombre} <{self.email}>"
