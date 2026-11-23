"""Acceso de sólo lectura a la tabla existente (sin INSERT/UPDATE/DELETE)."""
from urllib.parse import quote_plus
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from modulos.sql_query import CONSULTA_DNI


@st.cache_resource(show_spinner=False)
def motor_sql():
    cadena = str(st.secrets["sql"]["connection_string"])
    return create_engine(
        "mssql+pyodbc:///?odbc_connect=" + quote_plus(cadena),
        pool_pre_ping=True,
        connect_args={"timeout": 15},
    )


def buscar_derivaciones(dni: str, periodo: str) -> pd.DataFrame:
    if len(dni) != 8 or not dni.isascii() or not dni.isdecimal():
        raise ValueError("DNI inválido")
    if len(periodo) != 6 or not periodo.isascii() or not periodo.isdecimal():
        raise ValueError("Período inválido")
    with motor_sql().connect() as conexion:
        df = pd.read_sql_query(
            CONSULTA_DNI,
            conexion,
            params={"periodo": periodo, "dni": dni},
        )
    if "DNI_Cliente" in df.columns:
        df["DNI_Cliente"] = df["DNI_Cliente"].astype("string")
    return df
