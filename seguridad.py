"""Hash y verificación de contraseñas (sólo biblioteca estándar)."""
import hashlib
import hmac
import os

from dominio.excepciones import PasswordInvalidaError

_ALGORITMO = "pbkdf2_sha256"
_ITERACIONES = 200_000
LARGO_MINIMO = 8


def validar_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < LARGO_MINIMO:
        raise PasswordInvalidaError(
            f"La contraseña debe tener al menos {LARGO_MINIMO} caracteres.")


def hashear_password(password: str) -> str:
    """Devuelve 'algoritmo$iteraciones$salt$hash' con salt aleatorio."""
    validar_password(password)
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERACIONES)
    return f"{_ALGORITMO}${_ITERACIONES}${salt.hex()}${h.hex()}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        algoritmo, iteraciones, salt_hex, hash_hex = almacenado.split("$")
        if algoritmo != _ALGORITMO:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"),
            bytes.fromhex(salt_hex), int(iteraciones))
    except ValueError:
        return False
    return hmac.compare_digest(calculado.hex(), hash_hex)
