# INTEGRA | Actualización MSAL (sin rehacer el repositorio)

**Cambios:** solo reemplazar `app.py`, `modulos/auth.py`, `requirements.txt`, y añadir `msal_login/index.html`. No modificar `usuarios_autorizados.xlsx` (conserva los accesos ya agregados), `modulos/permisos.py`, `modulos/consulta.py`, `modulos/periodo.py`, `modulos/sql_query.py`, `assets` ni `.streamlit/config.toml`.

Este método recupera la lógica del archivo **MSAL original** aportado por el equipo: `client_id`, `tenant_id`, `redirect_uri` en `[msal]`, con verificación de token en Microsoft Graph (`User.Read`) y lista blanca del Excel. No necesita `client_secret` ni `cookie_secret` (que pertenecían a la variante `st.login`).

## Streamlit Secrets (ejemplo sin credenciales)

```toml
[msal]
client_id = "ID_APP_PROPORCIONADO_POR_TI"
tenant_id = "ID_TENANT_DE_INTEGRA"
redirect_uri = "https://URL-EXACTA-NUEVA-APP.streamlit.app/"
```

**Microsoft Entra ID debe registrar esta nueva URL como Redirect URI de tipo SPA**, además de conservar la del aplicativo original. Debe coincidir exactamente con la que figurará en Secrets (incluida la `/` final). Confirmar con TI que el client ID de la aplicación existente puede usarse desde la nueva URL. Si no lo permite, TI deberá autorizar otra. No copiar la `redirect_uri` antigua, porque corresponde a otro sitio.

No copiar `[carsa_users]` ni `[github_feedback_final]` ni sus contraseñas/tokens. Revocar el GitHub PAT expuesto y cambiar credenciales expuestas si son vigentes.

No subir `secrets.toml` a GitHub. Las consultas a SQL Server requieren una conexión aparte y alojamiento validado por TI; la aprobación del login Microsoft no confirma conectividad SQL ni cumplimiento del alojamiento para información real.

## Comprobaciones

- Módulos `modulos/consulta.py`, `modulos/periodo.py` y `modulos/sql_query.py` del repositorio actual permanecen intactos.
- El Excel mantiene los correos y roles que ya cargaste en GitHub.
- El login queda bloqueado si no hay configuración MSAL.
- El backend confirma cada token con Microsoft Graph y permite solo los correos de Integra incluidos en Excel.
- Nunca envía contraseñas o secretos de GitHub al navegador.
