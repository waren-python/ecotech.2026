"""Clase base abstracta Usuario (UML: Usuario <|-- Empleado, Administrador)."""
import re
from abc import ABC, abstractmethod

from dominio.excepciones import NombreInvalidoError
from dominio.seguridad import verificar_password

_PATRON_NOMBRE_USUARIO = re.compile(r"^[A-Za-z0-9_.]{3,30}$")


class Usuario(ABC):
    ROL = ""  # cada subclase declara su rol

    def __init__(self, nombre_usuario: str, password_hash: str,
                 id_usuario: int | None = None):
        self._id_usuario = id_usuario
        self._nombre_usuario = ""
        self.nombre_usuario = nombre_usuario      # pasa por la validación
        self._password_hash = password_hash       # nunca la contraseña en claro

    # --- encapsulamiento ---------------------------------------------------
    @property
    def id_usuario(self) -> int | None:
        return self._id_usuario

    def asignar_id(self, id_usuario: int | None) -> None:
        """Lo usa el repositorio al persistir (o al revertir) el objeto."""
        self._id_usuario = id_usuario

    @property
    def nombre_usuario(self) -> str:
        return self._nombre_usuario

    @nombre_usuario.setter
    def nombre_usuario(self, valor: str) -> None:
        if not isinstance(valor, str) or not _PATRON_NOMBRE_USUARIO.match(valor):
            raise NombreInvalidoError(
                "El nombre de usuario debe tener 3 a 30 caracteres "
                "(letras, números, '_' o '.').")
        self._nombre_usuario = valor

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def rol(self) -> str:
        return self.ROL

    # --- comportamiento común (herencia) ------------------------------------
    def autenticar(self, password: str) -> bool:
        return verificar_password(password, self._password_hash)

    def tiene_acceso(self, modulo: str) -> bool:
        return modulo in self.modulos_permitidos()

    # --- comportamiento que cada subclase redefine (polimorfismo) ----------
    @abstractmethod
    def modulos_permitidos(self) -> frozenset:
        ...

    @abstractmethod
    def descripcion(self) -> str:
        ...

    def resumen(self) -> str:
        return f"[{self.rol}] {self.nombre_usuario}: {self.descripcion()}"

    def __eq__(self, otro) -> bool:
        return (type(self) is type(otro)
                and self.nombre_usuario == otro.nombre_usuario)

    def __hash__(self) -> int:
        return hash((self.ROL, self.nombre_usuario))
