"""Administrador: usuario con acceso a todos los módulos de gestión."""
from collections import defaultdict

from dominio.excepciones import DatoInvalidoError
from dominio.informe import Informe
from dominio.usuario import Usuario


class Administrador(Usuario):
    ROL = "ADMINISTRADOR"
    TIPOS_INFORME = ("horas_por_empleado",)

    def __init__(self, nombre_usuario: str, password_hash: str,
                 area_responsable: str, id_usuario: int | None = None):
        super().__init__(nombre_usuario, password_hash, id_usuario)
        if not isinstance(area_responsable, str) or not area_responsable.strip():
            raise DatoInvalidoError("El área responsable es obligatoria.")
        self._area_responsable = area_responsable.strip()

    @property
    def area_responsable(self) -> str:
        return self._area_responsable

    def gestionar_departamentos(self, departamentos) -> list:
        """Resumen de dotación por departamento (lógica de dominio pura)."""
        return [f"{d.nombre} (gerente: {d.gerente}): {len(d.empleados)} empleado(s)"
                for d in departamentos]

    def generar_informe(self, tipo: str, empleados) -> Informe:
        """Dependencia con Informe: lo crea, pero no lo conserva como atributo."""
        if tipo not in self.TIPOS_INFORME:
            raise DatoInvalidoError(
                f"Tipo de informe desconocido. Use: {', '.join(self.TIPOS_INFORME)}.")
        acumulado = defaultdict(float)
        for empleado in empleados:
            for registro in empleado.registros:
                acumulado[(empleado.nombre, registro.proyecto.nombre)] += registro.horas_trabajadas
        filas = [{"empleado": e, "proyecto": p, "horas": h}
                 for (e, p), h in sorted(acumulado.items())]
        return Informe(tipo, filas)

    def modulos_permitidos(self) -> frozenset:
        return frozenset({"perfil", "proyectos",
                          "empleados", "departamentos", "gestion_proyectos",
                          "informes"})

    def descripcion(self) -> str:
        return f"área {self.area_responsable}"
