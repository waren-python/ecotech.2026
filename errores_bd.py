"""Traducción de errores crudos de sqlite3 al vocabulario del negocio."""
import sqlite3

from dominio.excepciones import (DatoInvalidoError, DuplicadoError, EmailDuplicadoError,
                                 ErrorPersistencia, NombreDuplicadoError,
                                 NombreUsuarioDuplicadoError, ReferenciaInvalidaError)


def traducir_error_sqlite(error: sqlite3.Error) -> ErrorPersistencia | DatoInvalidoError:
    mensaje = str(error)
    if isinstance(error, sqlite3.IntegrityError):
        if "UNIQUE" in mensaje:
            if "usuario.nombre_usuario" in mensaje:
                return NombreUsuarioDuplicadoError("Ese nombre de usuario ya existe.")
            if "empleado.email" in mensaje:
                return EmailDuplicadoError("Ya existe un empleado con ese email.")
            if "departamento.nombre" in mensaje or "proyecto.nombre" in mensaje:
                return NombreDuplicadoError("Ya existe un registro con ese nombre.")
            return DuplicadoError("El registro ya existe.")
        if "FOREIGN KEY" in mensaje:
            return ReferenciaInvalidaError(
                "La referencia no existe o el registro tiene datos asociados.")
        if "CHECK" in mensaje:
            return DatoInvalidoError("El dato no cumple las restricciones de la base de datos.")
    return ErrorPersistencia("Error de base de datos.")
