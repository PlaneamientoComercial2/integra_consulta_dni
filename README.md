# INTEGRA | Consulta DNI — únicamente cuentas INTEGRA

Actualización de la versión existente `integra_consulta_dni`: NO es otro aplicativo.

## Lista de acceso
`usuarios_autorizados.xlsx` contiene **cinco ADMIN** de @integraretail.pe. Para añadir la cuenta de prueba que habilite TI, agregar una fila con `CORREO`, `AGENCIA=TODAS`, `ROL=SUPERVISOR` (o ADMIN si TI lo define). Se rechazará toda cuenta `@alfinbanco.pe` incluso si se escribe por error en Excel.

## Función
- Login Microsoft de tenant Integra, validando el token + la lista de Excel.
- Una búsqueda por DNI de ocho dígitos, incluso los ceros iniciales.
- Consulta SELECT parametrizada a `PC.INTEGRA_DERIVACIONES`, `Periodo` automático (días 1–5 mes anterior, desde 6 mes actual), orden por `Fecha_Registro`.
- Solo lectura, sin botones para modificar/cargar/descargar.

## Actualizar proyecto en GitHub (NO crear otro)
Reemplazar `app.py`, `modulos/auth.py`, `modulos/permisos.py`, `usuarios_autorizados.xlsx` y `README.md` por estos archivos. El resto se conserva. Los archivos de `tests` permiten volver a validar lógica.

## Microsoft / SQL: integración pendiente
La app `Feedback_integra_externos` sirve de referencia visual y de cuenta Microsoft, pero su registro original no garantiza autorización para un NUEVO redirect URI. TI debe confirmar `client_id`, `client_secret` y `redirect_uri` del aplicativo nuevo, y configurar secretos privados del hosting. La versión usa `st.login()` con OIDC, no el componente MSAL personalizado. Esos dos flujos no son intercambiables sin configuración. También se requiere una conexión SQL de solo lectura alcanzable desde el servidor del aplicativo y un driver ODBC instalado en él.

**No se han probado credenciales de Microsoft ni SQL corporativo desde este entorno.** El uso real de datos personales debe estar expresamente autorizado para la modalidad y el alojamiento concretos de Streamlit.

## Verificación local
`python -m unittest discover -s tests -v` (requiere pandas, sqlalchemy, openpyxl).
