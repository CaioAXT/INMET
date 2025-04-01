import streamlit as st
import plotly.express as px


if st.session_state.df_diretriz is None:
    map_center = st.session_state.df_pontos
else:
    st.dataframe(st.session_state.df_diretriz, hide_index=True)
    map_center = st.session_state.df_diretriz
    map_center["Classificação do Ponto"] = map_center["Classificação do Ponto"].fillna(
        "Fora do Buffer"
    )

map_center = map_center[map_center["Estacao"].str.contains("Criosfera|Arq") == False]

st.sidebar.title("Mapa de Estações")

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
else:
    if st.session_state.df_diretriz is None:
        fig = px.scatter_mapbox(
            map_center,
            lat="Longitude",
            lon="Latitude",
            hover_name="Estacao",
            color="Classificação do Ponto",
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
