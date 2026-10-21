import unittest
from datetime import date

from dominio.departamento import Departamento
from dominio.excepciones import (AsignacionInvalidaError, CredencialesInvalidasError,
                                 EmailDuplicadoError, EmpleadoNoEncontradoError)
from dominio.proyecto import Proyecto
from dominio.seguridad import hashear_password
from dominio.administrador import Administrador
from pruebas.base import BaseBDTest, nuevo_empleado
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio
from repositorio.registro_repo import RegistroRepositorio
from repositorio.usuario_repo import UsuarioRepositorio


class TestCRUD(BaseBDTest):
    def test_crud_empleado_completo(self):
        repo = EmpleadoRepositorio(self.conn)
        e = repo.guardar(nuevo_empleado())
        self.assertIsNotNone(e.id_usuario)
        leido = repo.obtener_por_id(e.id_usuario)
        self.assertEqual(leido.email, "ana@ecotech.cl")
        leido.actualizar_datos({"telefono": "987654321"})
        repo.actualizar(leido)
        self.assertEqual(repo.obtener_por_id(e.id_usuario).telefono, "987654321")
        repo.eliminar(e.id_usuario)
        with self.assertRaises(EmpleadoNoEncontradoError):
            repo.obtener_por_id(e.id_usuario)

    def test_crud_departamento_y_agregacion(self):
        er, dr = EmpleadoRepositorio(self.conn), DepartamentoRepositorio(self.conn)
        e = er.guardar(nuevo_empleado())
        d = dr.guardar(Departamento("I+D", "Román Rojas"))
        dr.agregar_empleado(d, e)
        with self.assertRaises(AsignacionInvalidaError):
            dr.agregar_empleado(d, e)
        self.assertEqual(len(dr.obtener_por_id(d.id_departamento).empleados), 1)
        dr.eliminar(d.id_departamento)                 # el empleado sigue existiendo
        self.assertIsNotNone(er.obtener_por_id(e.id_usuario))

    def test_crud_proyecto_y_registro_de_horas(self):
        er, pr, rr = (EmpleadoRepositorio(self.conn), ProyectoRepositorio(self.conn),
                      RegistroRepositorio(self.conn))
        e = er.guardar(nuevo_empleado())
        p = pr.guardar(Proyecto("Monitoreo", "App energía", date(2021, 10, 9)))
        reg = e.registrar_horas(date(2026, 10, 1), 8, "Pruebas", p)
        with self.assertRaises(AsignacionInvalidaError):   # aún no asignado
            rr.guardar(reg)
        er.asignar_a_proyecto(e.id_usuario, p.id_proyecto)
        rr.guardar(reg)
        er.cargar_registros(e)
        self.assertEqual(e.total_horas(), 8.0)

    def test_autenticacion(self):
        ur = UsuarioRepositorio(self.conn)
        ur.guardar_administrador(
            Administrador("admin", hashear_password("Clave-Segura-1"), "TI"))
        self.assertEqual(ur.autenticar("admin", "Clave-Segura-1").rol, "ADMINISTRADOR")
        with self.assertRaises(CredencialesInvalidasError):
            ur.autenticar("admin", "mala")
        with self.assertRaises(CredencialesInvalidasError):
            ur.autenticar("no-existe", "Clave-Segura-1")


class TestInyeccionSQL(BaseBDTest):
    PAYLOAD = "' OR '1'='1"

    def test_payload_no_devuelve_datos(self):
        repo = EmpleadoRepositorio(self.conn)
        repo.guardar(nuevo_empleado())
        self.assertIsNone(repo.buscar_por_email(self.PAYLOAD))

    def test_payload_en_login_no_autentica(self):
        UsuarioRepositorio(self.conn).guardar_administrador(
            Administrador("admin", hashear_password("Clave-Segura-1"), "TI"))
        with self.assertRaises(CredencialesInvalidasError):
            UsuarioRepositorio(self.conn).autenticar(self.PAYLOAD, self.PAYLOAD)

    def test_tablas_intactas_tras_payload_destructivo(self):
        repo = EmpleadoRepositorio(self.conn)
        repo.guardar(nuevo_empleado())
        repo.buscar_por_email("x'; DROP TABLE empleado; --")
        self.assertEqual(self.contar("empleado"), 1)


class TestTransaccionAtomica(BaseBDTest):
    def test_rollback_si_falla_segunda_escritura(self):
        repo = EmpleadoRepositorio(self.conn)
        repo.guardar(nuevo_empleado())
        antes = self.contar("usuario")
        duplicado = nuevo_empleado(usuario="otro.usuario", email="ana@ecotech.cl")
        with self.assertRaises(EmailDuplicadoError):    # falla el INSERT en empleado
            repo.guardar(duplicado)
        self.assertEqual(self.contar("usuario"), antes)  # el INSERT en usuario se deshizo
        self.assertIsNone(duplicado.id_usuario)


if __name__ == "__main__":
    unittest.main()
