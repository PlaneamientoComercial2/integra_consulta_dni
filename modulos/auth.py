"""Acceso Microsoft Entra (único tenant INTEGRA), con autorización Excel."""
from pathlib import Path
from uuid import UUID
import time
import streamlit as st
from modulos.permisos import leer_permisos, validar_acceso

RUTA = Path(__file__).resolve().parent.parent / "usuarios_autorizados.xlsx"

@st.cache_data(ttl=60, show_spinner=False)
def usuarios_autorizados():
    return leer_permisos(RUTA)


def autenticacion_configurada() -> bool:
    """Fall closed: no mostrar login si la configuración OIDC está incompleta."""
    try:
        auth = st.secrets["auth"]
        acceso = st.secrets["acceso"]
        tenant = str(acceso["tenant_integra"]).strip().lower()
        UUID(tenant)
        return all(bool(auth.get(k)) for k in (
            "redirect_uri", "cookie_secret", "client_id",
            "client_secret", "server_metadata_url")) and (
            f"/{tenant}/" in str(auth["server_metadata_url"]).lower()
        )
    except (KeyError, ValueError, TypeError, AttributeError, FileNotFoundError):
        return False


def cuenta_actual():
    """Permitir solo un correo del Excel validado en el tenant de Integra."""
    if not st.user.is_logged_in:
        return None
    try:
        vencimiento = st.user.get("exp")
        if vencimiento is not None and float(vencimiento) <= time.time():
            return None
        correo = str(st.user.get("email") or st.user.get("preferred_username") or "")
        tid = str(st.user.get("tid") or "")
        tenant = str(st.secrets["acceso"]["tenant_integra"])
        return validar_acceso(correo, tid, tenant, usuarios_autorizados())
    except (KeyError, ValueError, TypeError, AttributeError, FileNotFoundError):
        return None
