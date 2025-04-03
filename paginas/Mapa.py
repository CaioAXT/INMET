import streamlit as st
import plotly.express as px
from funcoes.buscarbase import BuscarEstacoes
import pandas as pd

st.session_state.estacoes = BuscarEstacoes()

st.session_state.estacoes = st.session_state.estacoes[
    ~st.session_state.estacoes["Estacao"].isin(list(st.session_state.df_pontos))
]

if st.session_state.df_diretriz is None:
    map_center = st.session_state.df_pontos
else:
    coluna_com_ponto = next(
        (col for col in st.session_state.df_diretriz.columns if "Ponto" in col), None
    )
    st.sidebar.title("Mapa de Estações")
    st.sidebar.dataframe(st.session_state.df_pontos, hide_index=True)

    map_center = st.session_state.df_diretriz
    map_center = pd.concat(
        [
            st.session_state.estacoes,
            map_center,
        ],
        ignore_index=True,
    )
    map_center[f"{coluna_com_ponto}"] = map_center[f"{coluna_com_ponto}"].fillna(
        "Fora do Buffer"
    )

map_center = map_center[map_center["Estacao"].str.contains("Criosfera|Arq") == False]


if st.session_state.df_diretriz is None:
    fig = px.scatter_mapbox(
        map_center,
        lat="Longitude",
        lon="Latitude",
        hover_name="Estacao",
        zoom=3,
        center={
            "lat": map_center["Longitude"].mean(),
            "lon": map_center["Latitude"].mean(),
        },
        height=1200,
        size_max=2,
    )

elif st.session_state.df_diretriz is not None:
    fig = px.scatter_mapbox(
        map_center,
        lat="Longitude",
        lon="Latitude",
        hover_name="Estacao",
        color=f"{coluna_com_ponto}",
        zoom=3,
        center={
            "lat": map_center["Longitude"].mean(),
            "lon": map_center["Latitude"].mean(),
        },
        height=1200,
        size_max=2,
    )


fig.update_traces(marker=dict(size=10))
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

st.plotly_chart(fig)
