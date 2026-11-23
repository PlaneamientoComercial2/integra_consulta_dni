"""Integración con autenticación OIDC nativa de Streamlit (Microsoft Entra)."""
from pathlib import Path
from uuid import UUID
import time
import streamlit as st
from modulos.permisos import leer_permisos, validar_acceso

RUTA = Path(__file__).resolve().parent.parent / "usuarios_autorizados.xlsx"


@st.cache_data(ttl=60, show_spinner=False)
def usuarios_autorizados():
    return leer_permisos(RUTA)


def autenticacion_configurada():
    """Si faltan secretos, mostrar aviso y NO intentar abrir un login inválido."""
    try:
        acceso = st.secrets["acceso"]
        auth = st.secrets["auth"]
        for nombre in ("tenant_integra", "tenant_alfin"):
            if str(UUID(str(acceso[nombre]))) != str(acceso[nombre]).strip().lower():
                return False
        if acceso["tenant_integra"] == acceso["tenant_alfin"]:
            return False
        if not auth.get("redirect_uri") or not auth.get("cookie_secret"):
            return False
        for nombre in ("integra", "alfin"):
            proveedor = auth[nombre]
            if not all(proveedor.get(c) for c in ("client_id", "client_secret", "server_metadata_url")):
                return False
        return True
    except (KeyError, ValueError, TypeError, FileNotFoundError, AttributeError):
        return False


def cuenta_actual():
    if not st.user.is_logged_in:
        return None
    # El proveedor ha verificado el token OIDC. No se confía en la entrada manual.
    try:
        vencimiento = st.user.get("exp")
        if not vencimiento or float(vencimiento) <= time.time():
            return None
        correo = st.user.get("email") or st.user.get("preferred_username") or ""
        tenant = st.user.get("tid") or ""
        config = st.secrets["acceso"]
        tenants = {
            "integraretail.pe": str(config["tenant_integra"]),
            "alfinbanco.pe": str(config["tenant_alfin"]),
        }
        return validar_acceso(correo, tenant, tenants, usuarios_autorizados())
    except (KeyError, ValueError, TypeError, FileNotFoundError):
        return None
