"""Informe: datos consolidados exportables (dependencia desde Administrador)."""
import csv
from datetime import datetime

from dominio.excepciones import ExportacionError, FormatoNoSoportadoError

COLUMNAS = ("empleado", "proyecto", "horas")


class Informe:
    def __init__(self, tipo: str, filas: list, fecha_generacion: datetime | None = None):
        self._tipo = tipo
        self._filas = list(filas)
        self._fecha_generacion = fecha_generacion or datetime.now()

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def fecha_generacion(self) -> datetime:
        return self._fecha_generacion

    @property
    def filas(self) -> tuple:
        return tuple(self._filas)

    def exportar(self, formato: str, ruta: str) -> str:
        exportadores = {"csv": self._escribir_csv, "txt": self._escribir_txt}
        exportador = exportadores.get(str(formato).lower())
        if exportador is None:
            raise FormatoNoSoportadoError(
                f"Formato '{formato}' no soportado. Use: {', '.join(exportadores)}.")
        try:
            # utf-8-sig y ';' para que Excel en español abra el CSV sin ajustes
            with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
                exportador(archivo)
        except OSError as error:
            raise ExportacionError(f"No se pudo escribir '{ruta}'.") from error
        return ruta

    def _escribir_csv(self, archivo) -> None:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(COLUMNAS)
        for fila in self._filas:
            escritor.writerow([fila[c] for c in COLUMNAS])

    def _escribir_txt(self, archivo) -> None:
        archivo.write(f"Informe: {self.tipo} — {self.fecha_generacion:%d-%m-%Y %H:%M}\n")
        for fila in self._filas:
            archivo.write(f"{fila['empleado']} | {fila['proyecto']} | {fila['horas']:g} h\n")
