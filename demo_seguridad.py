"""Evidencia para el informe: inyección SQL y transacción atómica (BD temporal).
Ejecutar desde la raíz:  python -m pruebas.demo_seguridad"""
import contextlib
import os
import tempfile

from pruebas.base import nuevo_empleado
from repositorio.conexion import conectar, inicializar_bd
from repositorio.empleado_repo import EmpleadoRepositorio
from dominio.excepciones import EcoTechError

PAYLOAD = "' OR '1'='1"


def contar(conn, sql):
    return conn.execute(sql).fetchone()[0]


with tempfile.TemporaryDirectory() as carpeta:
    ruta = os.path.join(carpeta, "evidencia.db")
    inicializar_bd(ruta)
    with contextlib.closing(conectar(ruta)) as conn:
        repo = EmpleadoRepositorio(conn)
        repo.guardar(nuevo_empleado("ana.perez", "ana@ecotech.cl", "Ana Pérez"))
        repo.guardar(nuevo_empleado("luis.soto", "luis@ecotech.cl", "Luis Soto"))

        print("=== PRUEBA 1: inyección SQL ===")
        print(f"Empleados en la BD: {contar(conn, 'SELECT COUNT(*) FROM empleado')}")
        print(f"Payload enviado como email: {PAYLOAD!r}")
        ilustracion = "SELECT * FROM empleado WHERE email = '{}'".format(PAYLOAD)
        print(f"Si se concatenara, el motor recibiría: {ilustracion}  -> devolvería TODOS los empleados")
        resultado = repo.buscar_por_email(PAYLOAD)
        print(f"Resultado real con consulta parametrizada: {resultado}")
        repo.buscar_por_email("x'; DROP TABLE empleado; --")
        print(f"Tras payload destructivo, empleados en la BD: {contar(conn, 'SELECT COUNT(*) FROM empleado')}")

        print("\n=== PRUEBA 2: transacción atómica (commit / rollback) ===")
        antes = contar(conn, "SELECT COUNT(*) FROM usuario")
        print(f"Filas en usuario ANTES: {antes}")
        intruso = nuevo_empleado("otro.usuario", "ana@ecotech.cl", "Otra Persona")  # email repetido
        try:
            repo.guardar(intruso)
        except EcoTechError as error:
            print(f"Segunda escritura falló -> {type(error).__name__}: {error}")
        despues = contar(conn, "SELECT COUNT(*) FROM usuario")
        print(f"Filas en usuario DESPUÉS: {despues}  (rollback deshizo el INSERT en usuario)")
        print(f"ID asignado al objeto tras el fallo: {intruso.id_usuario}")
