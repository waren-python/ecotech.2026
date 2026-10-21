"""Utilidades de prueba: base temporal aislada por test."""
import contextlib
import os
import tempfile
import unittest
from datetime import date

from dominio.empleado import Empleado
from dominio.seguridad import hashear_password
from repositorio.conexion import conectar, inicializar_bd


def nuevo_empleado(usuario="ana.perez", email="ana@ecotech.cl", nombre="Ana Pérez"):
    return Empleado(usuario, hashear_password("Clave-Segura-1"), nombre,
                    "Av. Verde 123, Concepción", "+56 9 1234 5678", email,
                    date(2022, 7, 14), 790800)


class BaseBDTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self._dir.name, "test.db")
        inicializar_bd(self.ruta)
        self.conn = conectar(self.ruta)

    def tearDown(self):
        self.conn.close()
        self._dir.cleanup()

    def contar(self, tabla):
        tablas = {"usuario": "SELECT COUNT(*) FROM usuario",
                  "empleado": "SELECT COUNT(*) FROM empleado"}
        return self.conn.execute(tablas[tabla]).fetchone()[0]
