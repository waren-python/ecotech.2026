"""Auditoría estática: toda llamada execute()/executemany() debe recibir un
literal de texto (ni f-strings, ni concatenación, ni formato %, ni .format)."""
import ast
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def auditar() -> int:
    llamadas = infracciones = 0
    for archivo in sorted(RAIZ.rglob("*.py")):
        if "pruebas" in archivo.parts:
            continue
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
                    and nodo.func.attr in ("execute", "executemany") and nodo.args):
                llamadas += 1
                primero = nodo.args[0]
                if not (isinstance(primero, ast.Constant) and isinstance(primero.value, str)):
                    infracciones += 1
                    print(f"INFRACCIÓN {archivo.relative_to(RAIZ)}:{nodo.lineno}")
    print(f"Llamadas a execute auditadas: {llamadas} | Infracciones: {infracciones}")
    return infracciones


if __name__ == "__main__":
    sys.exit(1 if auditar() else 0)
