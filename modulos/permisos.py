"""Funciones de autorización. La identidad la verifica Microsoft OIDC vía Streamlit."""
from pathlib import Path
import pandas as pd

ROLES = {"ADMIN", "SUPERVISOR"}


def leer_permisos(ruta: str | Path) -> dict[str, str]:
    """Lee el Excel de usuarios; solo permite los roles expresamente habilitados."""
    datos = pd.read_excel(ruta, dtype=str).fillna("")
    datos.columns = [str(c).strip().upper() for c in datos.columns]
    if not {"CORREO", "ROL"}.issubset(datos.columns):
        raise ValueError("El Excel debe contener CORREO y ROL")
    permisos = {}
    for _, fila in datos.iterrows():
        correo = str(fila["CORREO"]).strip().lower()
        rol = str(fila["ROL"]).strip().upper()
        if correo and rol in ROLES:
            permisos[correo] = rol
    return permisos


def validar_acceso(correo: str, tid: str, tenants: dict[str, str], permisos: dict[str, str]):
    """Requiere email explícito + tenant Microsoft esperado para su dominio."""
    correo = str(correo or "").strip().lower()
    tid = str(tid or "").strip().lower()
    dominio = correo.rpartition("@")[2]
    if not dominio or not tid:
        return None
    tenant_esperado = str(tenants.get(dominio, "")).strip().lower()
    if not tenant_esperado or tid != tenant_esperado:
        return None
    rol = permisos.get(correo)
    if rol not in ROLES:
        return None
    return {"correo": correo, "rol": rol}
