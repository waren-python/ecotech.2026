"""Excepciones propias del dominio EcoTech (vocabulario del negocio)."""


class EcoTechError(Exception):
    """Excepción base para errores del sistema EcoTech."""


# --- Datos inválidos (también son ValueError) -------------------------------
class DatoInvalidoError(EcoTechError, ValueError):
    """Un dato ingresado no cumple las reglas del negocio."""


class NombreInvalidoError(DatoInvalidoError):
    """Nombre vacío, demasiado largo o con formato no permitido."""


class EmailInvalidoError(DatoInvalidoError):
    """El correo no tiene un formato válido."""


class TelefonoInvalidoError(DatoInvalidoError):
    """El teléfono no tiene entre 8 y 12 dígitos."""


class FechaInvalidaError(DatoInvalidoError):
    """Fecha ausente, futura o fuera de rango."""


class SalarioInvalidoError(DatoInvalidoError):
    """El salario no cumple las restricciones (mayor a 0 y bajo el tope)."""


class HorasInvalidasError(DatoInvalidoError):
    """Las horas trabajadas deben estar entre 0 (exclusivo) y 24."""


class PasswordInvalidaError(DatoInvalidoError):
    """La contraseña no cumple el largo mínimo."""


# --- Reglas de negocio ------------------------------------------------------
class AsignacionInvalidaError(EcoTechError):
    """Asignación imposible: duplicada, inexistente o empleado no asignado."""


class CredencialesInvalidasError(EcoTechError):
    """Usuario o contraseña incorrectos."""


class FormatoNoSoportadoError(EcoTechError):
    """Formato de exportación de informe no soportado."""


class ExportacionError(EcoTechError):
    """No fue posible escribir el archivo del informe."""


# --- Persistencia (traducidas desde sqlite3 por el repositorio) -------------
class ErrorPersistencia(EcoTechError):
    """Falla genérica de la capa de datos."""


class ConexionBDError(ErrorPersistencia):
    """No fue posible abrir o inicializar la base de datos."""


class RegistroNoEncontradoError(ErrorPersistencia):
    """No existe el registro solicitado."""


class EmpleadoNoEncontradoError(RegistroNoEncontradoError):
    pass


class DepartamentoNoEncontradoError(RegistroNoEncontradoError):
    pass


class ProyectoNoEncontradoError(RegistroNoEncontradoError):
    pass


class DuplicadoError(ErrorPersistencia):
    """Violación de unicidad."""


class EmailDuplicadoError(DuplicadoError):
    """Ya existe un empleado con ese email."""


class NombreUsuarioDuplicadoError(DuplicadoError):
    """Ya existe un usuario con ese nombre de usuario."""


class NombreDuplicadoError(DuplicadoError):
    """Ya existe un departamento o proyecto con ese nombre."""


class ReferenciaInvalidaError(ErrorPersistencia):
    """Referencia a un registro inexistente o con dependencias."""
