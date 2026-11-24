"""Inicio de sesión MSAL del sistema original; validación en Microsoft Graph.

No lee contraseñas de usuarios ni tokens de GitHub. El correo autenticado debe
figurar además en usuarios_autorizados.xlsx.
"""
from pathlib import Path
from uuid import UUID
from urllib.parse import urlparse
import time

import requests
import streamlit as st
import streamlit.components.v1 as components

from modulos.permisos import leer_permisos

BASE = Path(__file__).resolve().parent.parent
EXCEL = BASE / "usuarios_autorizados.xlsx"
MSAL_COMPONENT = BASE / "msal_login"

boton_ms = components.declare_component("msal_login_integra", path=str(MSAL_COMPONENT))


@st.cache_data(ttl=60, show_spinner=False)
def usuarios_autorizados():
    return leer_permisos(EXCEL)


def msal_configurado():
    try:
        cfg = st.secrets["msal"]
        UUID(str(cfg["client_id"]))
        UUID(str(cfg["tenant_id"]))
        url = urlparse(str(cfg["redirect_uri"]))
        return url.scheme == "https" and bool(url.netloc) and bool(url.path in ("", "/"))
    except (KeyError, ValueError, TypeError, AttributeError, FileNotFoundError):
        return False


def boton_microsoft():
    cfg = st.secrets["msal"]
    return boton_ms(client_id=str(cfg["client_id"]),
                    tenant_id=str(cfg["tenant_id"]),
                    redirect_uri=str(cfg["redirect_uri"]),
                    silent=False, key="msal_login", default=None)


def correo_token_validado(token):
    """Graph /me valida el access token; nunca confiar en el correo del navegador."""
    if not token or not isinstance(token, str):
        return ""
    try:
        r = requests.get("https://graph.microsoft.com/v1.0/me",
                         headers={"Authorization": f"Bearer {token}"}, timeout=12)
        if r.status_code != 200:
            return ""
        perfil = r.json()
        return str(perfil.get("mail") or perfil.get("userPrincipalName") or "").strip().lower()
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return ""


def iniciar_sesion_token(token):
    """Guardar solo una sesión autorizada y con hora de expiración conservadora."""
    correo = correo_token_validado(token)
    rol = usuarios_autorizados().get(correo)
    if not correo.endswith("@integraretail.pe") or rol not in {"ADMIN", "SUPERVISOR"}:
        return False
    st.session_state["msal_access_token"] = token
    st.session_state["msal_verified_email"] = correo
    st.session_state["msal_last_verified"] = time.time()
    return True


def cuenta_actual():
    """Revalidar con Graph antes de mostrar o consultar información."""
    token = st.session_state.get("msal_access_token")
    if not token:
        return None
    correo = correo_token_validado(token)
    if not correo or correo != st.session_state.get("msal_verified_email"):
        cerrar_sesion(rerun=False)
        return None
    rol = usuarios_autorizados().get(correo)
    if not correo.endswith("@integraretail.pe") or rol not in {"ADMIN", "SUPERVISOR"}:
        cerrar_sesion(rerun=False)
        return None
    st.session_state["msal_last_verified"] = time.time()
    return {"correo": correo, "rol": rol}


def cerrar_sesion(rerun=True):
    for k in ("msal_access_token", "msal_verified_email", "msal_last_verified",
              "resultado", "dni_consultado", "periodo_consultado"):
        st.session_state.pop(k, None)
    if rerun:
        st.rerun()
