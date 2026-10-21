import unittest
from datetime import date, timedelta

from dominio.administrador import Administrador
from dominio.excepciones import (DatoInvalidoError, EmailInvalidoError, HorasInvalidasError,
                                 SalarioInvalidoError)
from dominio.proyecto import Proyecto
from dominio.seguridad import hashear_password
from pruebas.base import nuevo_empleado


class TestDominio(unittest.TestCase):
    def test_salario_invalido(self):
        e = nuevo_empleado()
        with self.assertRaises(SalarioInvalidoError):
            e.salario = -5

    def test_email_invalido(self):
        with self.assertRaises(EmailInvalidoError):
            nuevo_empleado(email="sin-arroba")

    def test_actualizar_datos_todo_o_nada(self):
        e = nuevo_empleado()
        with self.assertRaises(DatoInvalidoError):
            e.actualizar_datos({"direccion": "Nueva 1", "telefono": "abc"})
        self.assertEqual(e.direccion, "Av. Verde 123, Concepción")

    def test_campo_no_editable(self):
        with self.assertRaises(DatoInvalidoError):
            nuevo_empleado().actualizar_datos({"salario": 1})

    def test_horas_fuera_de_rango_y_futuro(self):
        e = nuevo_empleado()
        p = Proyecto("App", "desc", date(2021, 10, 9))
        with self.assertRaises(HorasInvalidasError):
            e.registrar_horas(date.today(), 25, "x", p)
        with self.assertRaises(DatoInvalidoError):
            e.registrar_horas(date.today() + timedelta(days=1), 2, "x", p)

    def test_polimorfismo_modulos(self):
        admin = Administrador("root.admin", hashear_password("Clave-Segura-1"), "TI")
        usuarios = [nuevo_empleado(), admin]
        self.assertEqual([u.tiene_acceso("informes") for u in usuarios], [False, True])

    def test_password_hash_no_es_texto_plano(self):
        e = nuevo_empleado()
        self.assertNotIn("Clave-Segura-1", e.password_hash)
        self.assertTrue(e.autenticar("Clave-Segura-1"))
        self.assertFalse(e.autenticar("otra"))


if __name__ == "__main__":
    unittest.main()
