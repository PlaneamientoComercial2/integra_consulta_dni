"""Lista blanca de usuarios; nuevos accesos por Excel, solo dominio Integra."""
from pathlib import Path
import pandas as pd

ROLES = {"ADMIN", "SUPERVISOR"}
DOMINIO = "integraretail.pe"


def leer_permisos(ruta: str | Path) -> dict[str, str]:
    datos = pd.read_excel(ruta, dtype=str).fillna("")
    datos.columns = [str(c).strip().upper() for c in datos.columns]
    if not {"CORREO", "ROL"}.issubset(datos.columns):
        raise ValueError("El Excel debe contener CORREO y ROL")
    permisos = {}
    for _, fila in datos.iterrows():
        correo = str(fila["CORREO"]).strip().lower()
        rol = str(fila["ROL"]).strip().upper()
        if correo.endswith("@" + DOMINIO) and rol in ROLES:
            permisos[correo] = rol
    return permisos


def validar_acceso(correo: str, tid: str, tenant_integra: str, permisos: dict[str, str]):
    correo = str(correo or "").strip().lower()
    tid = str(tid or "").strip().lower()
    tenant = str(tenant_integra or "").strip().lower()
    if not correo.endswith("@" + DOMINIO) or not tid or tid != tenant:
        return None
    rol = permisos.get(correo)
    if rol not in ROLES:
        return None
    return {"correo": correo, "rol": rol}
