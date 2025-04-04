from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")


def BuscarBaseINMETporEstacoes(listaestacoes: list):
    conn_params = {
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
    }

    connection = psycopg2.connect(**conn_params)

    cursor = connection.cursor()
    cursor.execute(
        f"""
        SELECT "Data", "Hora", "RadiacaoGlobal", "VelocidadedoVento", "TemperaturaAr", "Estacao"
        FROM inmet
        WHERE "Estacao" IN ({', '.join(f"'{v}'" for v in listaestacoes)})
        """
    )

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    cursor.close()
    connection.close()
    return df


def BuscarEstacoes():
    conn_params = {
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
    }

    connection = psycopg2.connect(**conn_params)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT "Estacao", "Latitude", "Longitude"
        FROM inmetpontos
        """
    )

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    connection.close()
    return df
