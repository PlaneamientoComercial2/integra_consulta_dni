"""Regla: del 1 al 5 inclusive, mostrar mes anterior. Desde el 6, mes actual."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def periodo_habilitado(fecha: date | None = None) -> str:
    if fecha is None:
        fecha = datetime.now(ZoneInfo("America/Lima")).date()
    mes = fecha.replace(day=1) - timedelta(days=1) if fecha.day <= 5 else fecha
    return mes.strftime("%Y%m")
