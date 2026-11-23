# INTEGRA | Consulta de Derivaciones — revisión previa a publicación

Aplicación web Streamlit de consulta por DNI a la tabla `PC.INTEGRA_DERIVACIONES`.

## Qué se validó sin conectar a servidores corporativos

- Lista de **9 correos**: 5 ADMIN `@integraretail.pe`, 4 SUPERVISOR `@alfinbanco.pe`. Ambos roles pueden consultar solamente.
- DNI de 8 dígitos **como texto**, incluidos ceros iniciales.
- Regla de período con fecha local de Lima: días 1–5 muestra mes anterior; desde 6 muestra mes actual.
- `SELECT` parametrizado por período y DNI, ordenado por `Fecha_Registro ASC`.
- Sin funciones de descarga, modificación ni carga.
- Pruebas unitarias en `tests/` (fechas, permisos, consulta SQL con datos sintéticos).
- Corrección: Streamlit >= 1.60 para `client.disableDataExport`.
- Corrección: autenticación integrada `st.login` de Streamlit y Microsoft OIDC, sin login personalizado en iframe.

## Qué NO se puede confirmar aquí

**No se probó un inicio de sesión Microsoft ni una consulta SQL Server corporativa real.** Requiere aprobación/configuración de TI: registros de aplicaciones Microsoft, GUID de los dos tenants, `client_id`, `client_secret`, `redirect_uri`, servidor Streamlit autorizado y una conexión corporativa de solo lectura con ODBC.

**Importante:** Community Cloud no se debe utilizar con datos personales/financieros de clientes para fines comerciales, según los términos de Streamlit. Desplegar exclusivamente en hosting autorizado por TI.

## Cómo funciona

1. En la pantalla se elige **Microsoft Integra** o **Microsoft Alfin**. Es el mismo tipo de inicio de sesión corporativa; se elige según organización.
2. Streamlit comprueba el token OIDC y coloca la información en `st.user`.
3. El programa comprueba `tid` (tenant autorizado), `exp` (vencimiento), correo y rol contra `usuarios_autorizados.xlsx`.
4. Si está autorizado, el usuario escribe su DNI y ve los registros del período, sin descargas ni cambios.

## Administrar nuevos usuarios

Editar `usuarios_autorizados.xlsx` (`CORREO`, `AGENCIA`, `ROL`) y reemplazarlo en el repositorio privado, con `Commit changes`; autorización local con caché de hasta 60 segundos. No hace falta modificar Python **si la cuenta ya pertenece a uno de los dos tenants y Microsoft le permite iniciar sesión**. Si TI exige asignación individual a la aplicación, también debe dar el alta en Microsoft Entra; **el Excel no reemplaza la habilitación Microsoft**.

## Configuración del despliegue

- GitHub privado con `app.py`, `requirements.txt` en raíz.
- Copiar **solo los valores** de `.streamlit/secrets.EJEMPLO.toml` al gestor privado de secretos del servidor corporativo, no subir `secrets.toml` real.
- Microsoft Entra: registrar URI OIDC **tipo Web** `https://URL_APROBADA/oauth2callback` para ambos proveedores; tener consentimiento empresarial necesario.
- SQL Server: cuenta con permisos `SELECT` sobre la tabla (sin `INSERT`, `UPDATE`, `DELETE`), conexión segura y accesibilidad a SQL desde el servidor donde corre Streamlit.
- Instalar un ODBC SQL Server apropiado en el servidor, incluso si `pyodbc` ya se instaló.
- Si la app corre dentro de VPN/red interna, los usuarios deben acceder por un endpoint corporativo autorizado.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

La vista `VISTA_PREVIA.html` utiliza datos ficticios y no consulta SQL real.
