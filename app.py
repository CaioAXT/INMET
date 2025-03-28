import streamlit as st
from st_pages import add_page_title, get_nav_from_toml
import pandas as pd
import shutil
from funcoes.buscarbase import BuscarEstacoes

st.set_page_config(page_title="Estudos AXT", page_icon="📊", layout="wide")

nav = get_nav_from_toml(".streamlit/pages_sections.toml")

# region Cache
if "df_pontos" not in st.session_state or st.session_state.df_pontos is None:
    # Estações Selecionadas (dentro do buffer)
    st.session_state.df_pontos = BuscarEstacoes()

if "df_total" not in st.session_state:
    # Base completa do INMET com todas as estações selecionadas
    st.session_state.df_total = None

if "df_diretriz" not in st.session_state:
    # Estações + Vertices + Intermediários
    st.session_state.df_diretriz = None

if "df_clima" not in st.session_state:
    st.session_state.df_clima = None

if "df_pontos_vertices" not in st.session_state:
    # Vertices inseridos
    st.session_state.df_pontos_vertices = pd.DataFrame(
        columns=["Nome do Vertice", "Latitude", "Longitude"], data=[["P1", 0.0, 0.0]]
    )

if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "buffer": 0,
        "idnom": 0.0,
        "innom": 0.0,
        "vdnom": 0.0,
        "vnnom": 0.0,
        "idsobrec": 0.0,
        "insobrec": 0.0,
        "vdsobrec": 0.0,
        "vnsobrec": 0.0,
        "tensao": 0,
        "diamentrototal": 0.0,
        "diamentroaluminio": 0.0,
        "coefabsorsolar": 0.0,
        "condutor": "",
        "feixe": 0,
        "rdc20cc": 0.0,
        "epsilon": 0.0,
        "alturamediadalt": 0,
        "coefvarrestemp": 0.0,
        "tcnom_min": 20,
        "tcnom_max": 200,
    }
# endregion

st.logo("arquivoscomplementares\logo.webp")


import streamlit as st

# Supondo que @st.dialog("Resetar base?") seja um decorator
# que cria um "popup" ou "modal" personalizado.


@st.dialog("Resetar base?")
def resetar_base():
    st.warning(
        f"""O seguinte botão irá resetar a base de dados e limpar o cache do site. Incluindo:\n\n
- Vértices e Diretriz da linhas inseridos
- Dados de referência para o Estudo de Ampacidade
- Estações selecionadas para o Estudo de Clima.

        Não será possivel reverter essa operação.
        """
    )
    shutil.rmtree("funcoes/__pycache__", ignore_errors=True)
    if st.button("Sim, resetar agora", type="primary"):
        st.session_state.df_total = None
        st.success("Base resetada com sucesso!")


st.sidebar.button("Resetar Base / Limpar Cache", on_click=resetar_base, type="primary")

pg = st.navigation(nav)

add_page_title(pg)

pg.run()
