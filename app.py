"""INTEGRA — Consulta DNI. Microsoft Entra OIDC y SQL de solo lectura."""
from pathlib import Path
import streamlit as st
from modulos.auth import autenticacion_configurada, cuenta_actual
from modulos.consulta import buscar_derivaciones
from modulos.periodo import periodo_habilitado

BASE = Path(__file__).resolve().parent
LOGO = BASE / "assets" / "carsa_logo_transparente.png"

st.set_page_config(page_title="INTEGRA | Consulta de Derivaciones", page_icon="🔎", layout="wide", initial_sidebar_state="collapsed")
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


if not autenticacion_configurada():
    mostrar_logo(190)
    st.title("Consulta de Derivaciones")
    st.warning("La aplicación todavía no tiene configurado el acceso Microsoft de Integra y Alfin. Solicita a TI configurar los secretos corporativos antes de utilizarla.")
    st.stop()

if not st.user.is_logged_in:
    izquierda, centro, derecha = st.columns([1, 1.3, 1])
    with centro:
        mostrar_logo(300)
        st.title("Consulta de Derivaciones")
        st.caption("INTEGRA · Acceso con Microsoft · Solo usuarios autorizados")
        st.divider()
        st.write("Selecciona tu cuenta corporativa:")
        if st.button("Ingresar con Microsoft — Integra", type="primary", width="stretch"):
            st.login("integra")
        if st.button("Ingresar con Microsoft — Alfin", width="stretch"):
            st.login("alfin")
        st.caption("Ambas opciones utilizan el inicio de sesión Microsoft; no se crean contraseñas nuevas.")
    st.stop()

usuario = cuenta_actual()
if not usuario:
    st.error("Acceso no autorizado o sesión vencida.")
    if st.button("Cerrar sesión", type="primary"):
        st.logout()
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
        st.logout()

st.divider()
periodo = periodo_habilitado()
st.info(f"Período habilitado: {periodo}")

with st.form("form_dni"):
    st.write("**DNI del cliente**")
    dni = st.text_input("Ingresa 8 dígitos, incluyendo los ceros iniciales", max_chars=8, placeholder="00012345")
    consultar = st.form_submit_button("Consultar DNI", type="primary")

if consultar:
    dni = dni.strip()
    for clave in ("resultado", "dni_consultado", "periodo_consultado"):
        st.session_state.pop(clave, None)
    if len(dni) != 8 or not dni.isascii() or not dni.isdecimal():
        st.warning("Ingresa un DNI válido de 8 dígitos. Se respetan los ceros iniciales.")
    elif not cuenta_actual():
        st.error("La sesión venció o tu cuenta perdió la autorización. Vuelve a iniciar sesión.")
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

st.caption("Planeamiento Comercial · INTEGRA / Alfin Banco")
