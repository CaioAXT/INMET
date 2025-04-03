import oracledb
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")
ORACLE_USER = os.getenv("ORACLE_USER")


def BuscarBaseINMETporEstacoes(listaestacoes: list):

    connection = oracledb.connect(
        user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN
    )

    cursor = connection.cursor()
    cursor.execute(
        f"""
        SELECT "Data", "Hora", "RadiacaoGlobal", "VelocidadedoVento", "TemperaturaAr", "Estacao"
    FROM ENGENHARIA.INMET
    WHERE "Estacao" in ({', '.join(f"'{v}'" for v in listaestacoes)})
        """
    )

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    cursor.close()
    return df


def BuscarEstacoes():

    connection = oracledb.connect(
        user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN
    )

    cursor = connection.cursor()
    cursor.execute(
        f"""
        SELECT "Estacao", "Latitude", "Longitude"
        FROM ENGENHARIA.INMETESTACOES
        """
    )
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["Estacao", "Longitude", "Latitude"])
    cursor.close()
    return df
