# EcoTech Solutions — Sistema de Gestión de Empleados (UA2, TI3021)

Aplicación de consola en Python (POO + SQLite) que implementa el diagrama de clases UML de la ES1.

## Ejecución rápida
1. `python -m venv venv` y activar (`source venv/bin/activate` o `venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y definir `ECOTECH_ADMIN_PASSWORD` (mín. 8 caracteres)
4. `python main.py` (menú con login) · `python main.py --demo` (demostración automática)

## Pruebas y auditoría
- `python -m unittest discover -s . -t . -p "test_*.py" -v`
- `python pruebas/auditoria_sql.py` (verifica que ningún `execute` use concatenación/f-strings)
- `python -m pruebas.demo_seguridad` (evidencia de inyección SQL y rollback)

## Arquitectura
`dominio/` (POO pura, sin SQL) · `repositorio/` (SQL parametrizado + mapper) · `datos/schema.sql` · `main.py`
