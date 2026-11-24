"""INTEGRA | Consulta de Derivaciones. Solo Microsoft Integra + Excel autorizado."""
from pathlib import Path
from hmac import compare_digest
import streamlit as st
from modulos.auth import (msal_configurado, boton_microsoft, iniciar_sesion_token,
                          cuenta_actual, cerrar_sesion)
from modulos.consulta import buscar_derivaciones
from modulos.periodo import periodo_habilitado

BASE = Path(__file__).resolve().parent
LOGO = BASE / "assets" / "carsa_logo_transparente.png"

st.set_page_config(page_title="INTEGRA | Consulta de Derivaciones", page_icon="🔎",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #f8fafc;}
.block-container {max-width: 1270px; padding-top: 2rem;}
h1,h2,h3 {color: #172b4d !important;}
div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
 background: #d71920; border-color: #d71920; color: white; border-radius: 8px; font-weight: 650;
}
</style>
""", unsafe_allow_html=True)


def mostrar_logo(ancho=200):
    st.image(str(LOGO), width=ancho)


# MODO DE PRUEBA: sin cambiar de aplicativo ni abrir la consulta sin contraseña.
# Se activa/desactiva desde los Secrets de Streamlit; nunca se escribe la clave en GitHub.
try:
    MODO_PRUEBA = st.secrets.get("prueba", {}).get("habilitado", False) is True
except (KeyError, FileNotFoundError):
    MODO_PRUEBA = False

if MODO_PRUEBA:
    try:
        clave_prueba = str(st.secrets["prueba"]["clave"])
    except (KeyError, FileNotFoundError):
        st.error("Falta configurar [prueba].clave en los Secrets de Streamlit.")
        st.stop()

    if len(clave_prueba) < 24:
        st.error("La clave de prueba debe tener al menos 24 caracteres aleatorios.")
        st.stop()

    if not st.session_state.get("prueba_autorizada", False):
        mostrar_logo(190)
        st.title("Consulta de Derivaciones")
        st.warning("VALIDACIÓN TEMPORAL · Ingreso exclusivo con clave de prueba")
        with st.form("acceso_temporal"):
            clave_ingresada = st.text_input("Clave de validación", type="password")
            entrar = st.form_submit_button("Entrar a validar", type="primary")
        if entrar:
            if compare_digest(clave_ingresada, clave_prueba):
                st.session_state["prueba_autorizada"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta.")
        st.stop()
    usuario = {"correo": "Validación interna", "rol": "PRUEBA"}
else:
    if not msal_configurado():
        mostrar_logo(190)
        st.title("Consulta de Derivaciones")
        st.warning("Microsoft Integra pendiente. Configura [msal] en Secrets de Streamlit con los datos autorizados por TI.")
        st.stop()

    usuario = cuenta_actual()
    if not usuario:
        izquierda, centro, derecha = st.columns([1, 1.3, 1])
        with centro:
            mostrar_logo(300)
            st.title("Consulta de Derivaciones")
            st.caption("INTEGRA · Acceso con Microsoft · Solo usuarios autorizados")
            st.divider()
            st.write("Ingresa con tu cuenta corporativa Integra:")
            respuesta = boton_microsoft()
            if isinstance(respuesta, dict):
                if respuesta.get("token"):
                    if iniciar_sesion_token(respuesta["token"]):
                        st.rerun()
                    st.error("Cuenta no autorizada o token inválido. Consulta con TI.")
                elif respuesta.get("error"):
                    st.error("No fue posible iniciar sesión. Comprueba la autorización de la URL de retorno con TI.")
            st.caption("Solo cuentas @integraretail.pe incluidas en la lista de acceso.")
        st.stop()

encabezado, cuenta = st.columns([3, 1])
with encabezado:
    mostrar_logo(160)
    st.title("Consulta de Derivaciones")
    st.caption("INTEGRA · Visualización de registros por DNI")
with cuenta:
    st.caption("CUENTA AUTORIZADA")
    st.text(usuario["correo"])
    st.caption(f"Rol: {usuario['rol']} · Solo consulta")
    if st.button("Cerrar sesión"):
        if MODO_PRUEBA:
            st.session_state.clear()
            st.rerun()
        else:
            cerrar_sesion()

st.divider()
periodo = periodo_habilitado()
st.info(f"Período habilitado: {periodo}")
with st.form("form_dni"):
    st.write("**DNI del cliente**")
    dni = st.text_input("Ingresa 8 dígitos, incluyendo los ceros iniciales", max_chars=8,
                        placeholder="00012345")
    consultar = st.form_submit_button("Consultar DNI", type="primary")

if consultar:
    dni = dni.strip()
    for clave in ("resultado", "dni_consultado", "periodo_consultado"):
        st.session_state.pop(clave, None)
    if len(dni) != 8 or not dni.isascii() or not dni.isdecimal():
        st.warning("Ingresa un DNI válido de 8 dígitos. Se respetan los ceros iniciales.")
    elif not usuario or (not MODO_PRUEBA and not cuenta_actual()):
        st.error("La sesión perdió su autorización. Ingresa nuevamente.")
        st.stop()
    else:
        with st.spinner("Consultando derivaciones..."):
            try:
                df = buscar_derivaciones(dni, periodo)
            except Exception:
                st.error("No se pudo consultar SQL Server. Contacta al administrador de la aplicación.")
            else:
                st.session_state["resultado"] = df
                st.session_state["dni_consultado"] = dni
                st.session_state["periodo_consultado"] = periodo

if st.session_state.get("periodo_consultado") != periodo:
    st.session_state.pop("resultado", None)

if "resultado" in st.session_state:
    df = st.session_state["resultado"]
    st.subheader("Resultados")
    st.caption(f"DNI: {st.session_state['dni_consultado']} · Período: {periodo}")
    if df.empty:
        st.info("No hay registros para ese DNI en el período habilitado.")
    else:
        st.success(f"{len(df)} registros encontrados")
        st.dataframe(df, width="stretch", hide_index=True, height=min(580, 38 * (len(df) + 1) + 16))
        st.caption("Visualización de solo lectura. Sin botones de descarga, edición ni carga de archivos.")

st.caption("Planeamiento Comercial · Grupo CARSA | INTEGRA")
