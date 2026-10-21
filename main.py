"""EcoTech Solutions — Sistema de Gestión de Empleados (consola).

Uso:  python main.py          menú interactivo con inicio de sesión
      python main.py --demo   demostración automática (BD temporal)
"""
import contextlib
import getpass
import os
import sqlite3
import sys
import tempfile
from datetime import date

from dominio.administrador import Administrador
from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import DatoInvalidoError, EcoTechError
from dominio.proyecto import Proyecto
from dominio.seguridad import hashear_password
from repositorio.conexion import conectar, inicializar_bd
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio
from repositorio.registro_repo import RegistroRepositorio
from repositorio.usuario_repo import UsuarioRepositorio


# ---------------------------------------------------------------- entradas --
def pedir_texto(mensaje: str) -> str:
    return input(f"{mensaje}: ").strip()


def pedir_entero(mensaje: str) -> int:
    while True:
        try:
            return int(pedir_texto(mensaje))
        except ValueError:
            print("  ✗ Ingrese un número entero.")


def pedir_decimal(mensaje: str) -> float:
    while True:
        try:
            return float(pedir_texto(mensaje).replace(",", "."))
        except ValueError:
            print("  ✗ Ingrese un número (ej. 790800 o 7.5).")


def pedir_fecha(mensaje: str) -> date:
    while True:
        try:
            return date.fromisoformat(pedir_texto(f"{mensaje} (AAAA-MM-DD)"))
        except ValueError:
            print("  ✗ Fecha inválida. Use el formato AAAA-MM-DD.")


# -------------------------------------------------------- inicialización ----
def asegurar_administrador(conexion) -> None:
    repo = UsuarioRepositorio(conexion)
    if repo.existe_administrador():
        return
    usuario = os.getenv("ECOTECH_ADMIN_USUARIO", "admin")
    password = os.getenv("ECOTECH_ADMIN_PASSWORD", "")
    admin = Administrador(usuario, hashear_password(password), "Tecnologías de la Información")
    repo.guardar_administrador(admin)
    print(f"  Administrador inicial '{usuario}' creado desde variables de entorno.")


def iniciar_sesion(conexion):
    repo = UsuarioRepositorio(conexion)
    for _ in range(3):
        nombre = pedir_texto("Usuario")
        password = getpass.getpass("Contraseña: ")
        try:
            return repo.autenticar(nombre, password)
        except EcoTechError as error:
            print(f"  ✗ {error}")
    return None


# -------------------------------------------------------------- acciones ----
def registrar_empleado(conexion, _usuario):
    nombre_usuario = pedir_texto("Nombre de usuario")
    password = getpass.getpass("Contraseña (mín. 8 caracteres): ")
    empleado = Empleado(
        nombre_usuario, hashear_password(password), pedir_texto("Nombre completo"),
        pedir_texto("Dirección"), pedir_texto("Teléfono"), pedir_texto("Email"),
        pedir_fecha("Inicio de contrato"), pedir_decimal("Salario"))
    EmpleadoRepositorio(conexion).guardar(empleado)
    print(f"  ✓ Empleado registrado con ID {empleado.id_usuario}.")


def listar_empleados(conexion, _usuario):
    for e in EmpleadoRepositorio(conexion).listar_activos():
        print(f"  {e.id_usuario:>3} | {e.nombre} | {e.email} | ${e.salario:,.0f}")


def buscar_empleado(conexion, _usuario):
    e = EmpleadoRepositorio(conexion).buscar_por_email(pedir_texto("Email a buscar"))
    print(f"  {e.resumen()}" if e else "  Sin resultados.")


def actualizar_empleado(conexion, _usuario):
    repo = EmpleadoRepositorio(conexion)
    e = repo.obtener_por_id(pedir_entero("ID del empleado"))
    campo = pedir_texto("Campo (nombre/direccion/telefono/email)")
    e.actualizar_datos({campo: pedir_texto("Nuevo valor")})
    repo.actualizar(e)
    print("  ✓ Datos actualizados.")


def baja_empleado(conexion, _usuario):
    EmpleadoRepositorio(conexion).eliminar(pedir_entero("ID del empleado a dar de baja"))
    print("  ✓ Empleado dado de baja (se conserva su historial de horas).")


def crear_departamento(conexion, _usuario):
    d = DepartamentoRepositorio(conexion).guardar(
        Departamento(pedir_texto("Nombre"), pedir_texto("Gerente")))
    print(f"  ✓ Departamento creado con ID {d.id_departamento}.")


def listar_departamentos(conexion, usuario):
    repo = DepartamentoRepositorio(conexion)
    completos = [repo.obtener_por_id(d.id_departamento) for d in repo.listar()]
    for linea in usuario.gestionar_departamentos(completos):
        print(f"  {linea}")


def editar_departamento(conexion, _usuario):
    repo = DepartamentoRepositorio(conexion)
    d = repo.obtener_por_id(pedir_entero("ID del departamento"))
    d.nombre = pedir_texto("Nuevo nombre")
    d.gerente = pedir_texto("Nuevo gerente")
    repo.actualizar(d)
    print("  ✓ Departamento actualizado.")


def eliminar_departamento(conexion, _usuario):
    DepartamentoRepositorio(conexion).eliminar(pedir_entero("ID del departamento"))
    print("  ✓ Departamento eliminado (sus empleados quedan sin departamento).")


def asignar_a_departamento(conexion, _usuario):
    drepo = DepartamentoRepositorio(conexion)
    d = drepo.obtener_por_id(pedir_entero("ID del departamento"))
    e = EmpleadoRepositorio(conexion).obtener_por_id(pedir_entero("ID del empleado"))
    drepo.agregar_empleado(d, e)
    print(f"  ✓ {e.nombre} asignado a {d.nombre}.")


def crear_proyecto(conexion, _usuario):
    p = ProyectoRepositorio(conexion).guardar(Proyecto(
        pedir_texto("Nombre"), pedir_texto("Descripción"), pedir_fecha("Fecha de inicio")))
    print(f"  ✓ Proyecto creado con ID {p.id_proyecto}.")


def listar_proyectos(conexion, _usuario):
    repo = ProyectoRepositorio(conexion)
    for p in repo.listar():
        n = len(repo.obtener_por_id(p.id_proyecto).empleados)
        print(f"  {p.id_proyecto:>3} | {p.nombre} | inicio {p.fecha_inicio} | {n} empleado(s)")


def editar_proyecto(conexion, _usuario):
    repo = ProyectoRepositorio(conexion)
    p = repo.obtener_por_id(pedir_entero("ID del proyecto"))
    p.nombre = pedir_texto("Nuevo nombre")
    p.descripcion = pedir_texto("Nueva descripción")
    repo.actualizar(p)
    print("  ✓ Proyecto actualizado.")


def eliminar_proyecto(conexion, _usuario):
    ProyectoRepositorio(conexion).eliminar(pedir_entero("ID del proyecto"))
    print("  ✓ Proyecto eliminado.")


def asignar_a_proyecto(conexion, _usuario):
    EmpleadoRepositorio(conexion).asignar_a_proyecto(
        pedir_entero("ID del empleado"), pedir_entero("ID del proyecto"))
    print("  ✓ Asignación registrada.")


def desasignar_de_proyecto(conexion, _usuario):
    ok = EmpleadoRepositorio(conexion).desasignar_de_proyecto(
        pedir_entero("ID del empleado"), pedir_entero("ID del proyecto"))
    print("  ✓ Asignación eliminada." if ok else "  No existía esa asignación.")


def registrar_horas(conexion, usuario):
    proyecto = ProyectoRepositorio(conexion).obtener_por_id(pedir_entero("ID del proyecto"))
    registro = usuario.registrar_horas(
        pedir_fecha("Fecha"), pedir_decimal("Horas trabajadas"),
        pedir_texto("Descripción de la tarea"), proyecto)
    RegistroRepositorio(conexion).guardar(registro)
    print("  ✓ Horas registradas.")


def ver_mis_horas(conexion, usuario):
    EmpleadoRepositorio(conexion).cargar_registros(usuario)
    for r in usuario.registros:
        print(f"  {r}")
    print(f"  Total: {usuario.total_horas():g} h")


def exportar_informe(conexion, usuario):
    repo = EmpleadoRepositorio(conexion)
    empleados = [repo.cargar_registros(e) for e in repo.listar_activos()]
    informe = usuario.generar_informe("horas_por_empleado", empleados)
    formato = pedir_texto("Formato (csv/txt)").lower()
    ruta = informe.exportar(formato, f"informe_horas.{formato}")
    print(f"  ✓ Informe exportado en {ruta} ({len(informe.filas)} filas).")


def ver_perfil(_conexion, usuario):
    print(f"  {usuario.resumen()}")


# módulo requerido -> opciones; el menú se filtra con tiene_acceso() (polimorfismo)
OPCIONES = [
    ("perfil", "Ver mi perfil", ver_perfil),
    ("horas", "Registrar horas (proyecto asignado)", registrar_horas),
    ("horas", "Ver mis horas", ver_mis_horas),
    ("empleados", "Registrar empleado", registrar_empleado),
    ("empleados", "Listar empleados", listar_empleados),
    ("empleados", "Buscar empleado por email", buscar_empleado),
    ("empleados", "Actualizar datos de empleado", actualizar_empleado),
    ("empleados", "Dar de baja empleado", baja_empleado),
    ("departamentos", "Crear departamento", crear_departamento),
    ("departamentos", "Listar departamentos", listar_departamentos),
    ("departamentos", "Editar departamento", editar_departamento),
    ("departamentos", "Eliminar departamento", eliminar_departamento),
    ("departamentos", "Asignar empleado a departamento", asignar_a_departamento),
    ("proyectos", "Listar proyectos", listar_proyectos),
    ("gestion_proyectos", "Crear proyecto", crear_proyecto),
    ("gestion_proyectos", "Editar proyecto", editar_proyecto),
    ("gestion_proyectos", "Eliminar proyecto", eliminar_proyecto),
    ("gestion_proyectos", "Asignar empleado a proyecto", asignar_a_proyecto),
    ("gestion_proyectos", "Quitar empleado de proyecto", desasignar_de_proyecto),
    ("informes", "Generar y exportar informe de horas", exportar_informe),
]


def menu(conexion, usuario) -> None:
    disponibles = [o for o in OPCIONES if usuario.tiene_acceso(o[0])]
    while True:
        print(f"\n=== EcoTech · {usuario.resumen()} ===")
        for numero, (_, etiqueta, _) in enumerate(disponibles, start=1):
            print(f"  {numero:>2}. {etiqueta}")
        print("   0. Salir")
        eleccion = pedir_entero("Opción")
        if eleccion == 0:
            return
        if not 1 <= eleccion <= len(disponibles):
            print("  ✗ Opción fuera de rango.")
            continue
        try:
            disponibles[eleccion - 1][2](conexion, usuario)
        except EcoTechError as error:           # errores de negocio y de datos
            print(f"  ✗ {error}")
        except sqlite3.Error as error:          # falla del motor no traducida
            print(f"  ✗ Error de base de datos: {error}")


# ------------------------------------------------------------------ demo ----
def demo() -> None:
    """Recorre las operaciones clave en una BD temporal (para capturas)."""
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "demo.db")
        inicializar_bd(ruta)
        with contextlib.closing(conectar(ruta)) as conn:
            er, dr, pr, rr = (EmpleadoRepositorio(conn), DepartamentoRepositorio(conn),
                              ProyectoRepositorio(conn), RegistroRepositorio(conn))
            clave = hashear_password("Clave-Segura-1")
            admin = UsuarioRepositorio(conn).guardar_administrador(
                Administrador("admin", clave, "Tecnologías de la Información"))
            ana = er.guardar(Empleado("ana.perez", clave, "Ana Pérez", "Av. Verde 123",
                                      "+56912345678", "ana@ecotech.cl", date(2022, 7, 14), 790800))
            luis = er.guardar(Empleado("luis.soto", clave, "Luis Soto", "Calle Sol 45",
                                       "987654321", "luis@ecotech.cl", date(2023, 3, 1), 850000))
            dep = dr.guardar(Departamento("Investigación y Desarrollo", "Román Rojas"))
            dr.agregar_empleado(dep, ana)
            proy = pr.guardar(Proyecto("App de monitoreo energético", "Telemetría", date(2021, 10, 9)))
            er.asignar_a_proyecto(ana.id_usuario, proy.id_proyecto)
            rr.guardar(ana.registrar_horas(date(2026, 10, 15), 9, "Prueba del módulo de reportes", proy))
            print("1) Colección mixta, método común (polimorfismo):")
            for u in (admin, ana, luis):
                print("  ", u.resumen())
            print("2) CRUD: empleados activos:", [e.nombre for e in er.listar_activos()])
            print("3) Entrada inválida controlada:")
            for datos in ({"telefono": "abc"}, {"salario": 1}):
                try:
                    ana.actualizar_datos(datos)
                except DatoInvalidoError as error:
                    print(f"   ✗ {type(error).__name__}: {error}")
            print("4) Horas en proyecto no asignado:")
            try:
                rr.guardar(luis.registrar_horas(date(2026, 10, 15), 4, "Intento", proy))
            except EcoTechError as error:
                print(f"   ✗ {type(error).__name__}: {error}")
            informe = admin.generar_informe("horas_por_empleado", [er.cargar_registros(ana)])
            print("5) Informe:", list(informe.filas))


def main() -> int:
    if "--demo" in sys.argv:
        demo()
        return 0
    try:
        inicializar_bd()
        with contextlib.closing(conectar()) as conexion:
            asegurar_administrador(conexion)
            usuario = iniciar_sesion(conexion)
            if usuario is None:
                print("Demasiados intentos fallidos.")
                return 1
            menu(conexion, usuario)
    except EcoTechError as error:
        print(f"Error: {error}")
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nSesión finalizada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
