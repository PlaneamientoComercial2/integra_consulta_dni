"""Consulta parametrizada sin permisos de escritura."""
from sqlalchemy import text

CONSULTA_DNI = text("""
SELECT *
FROM PC.INTEGRA_DERIVACIONES
WHERE Periodo = :periodo
  AND DNI_Cliente = :dni
ORDER BY Fecha_Registro ASC
""")
