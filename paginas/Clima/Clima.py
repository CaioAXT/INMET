import streamlit as st
from funcoes.buscarbase import BuscarEstacoes, BuscarBaseINMETporEstacoes
from funcoes.funcoes import parse_to_float
import pandas as pd

st.text("")
if st.session_state.df_total is not None:

    col1, col2 = st.columns([3, 2])

    with col1:
        estacoesclima = st.multiselect(
            "Selecionar Estações", options=sorted(BuscarEstacoes()["Estacao"])
        )

    with col2:
        st.text("")
        usarampacidade = st.toggle("Usar Estações de Ampacidade", value=False)

    if st.session_state.df_clima is None:

        if st.button("Aplicar"):

            with st.spinner("Aguarde, estou consultando a Base do INMET..."):

                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)

else:
    estacoesclima = st.multiselect(
        "Selecionar Estações", options=sorted(BuscarEstacoes()["Estacao"])
    )
    if st.session_state.df_clima is None:

        if st.button("Aplicar"):

            with st.spinner("Aguarde, estou consultando a Base do INMET..."):

                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)
    else:
        if st.button("Atualizar"):
            with st.spinner("Aguarde, estou consultando a Base do INMET..."):
                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)

if st.session_state.df_clima is not None:
    estacoes = st.session_state.df_clima["Estacao"].unique()
    st.session_state.df_clima["TemperaturaAr"] = st.session_state.df_clima[
        "TemperaturaAr"
    ].apply(parse_to_float)
    st.session_state.df_clima = st.session_state.df_clima[
        (st.session_state.df_clima["RadiacaoGlobal"] != -9999)
        & (st.session_state.df_clima["TemperaturaAr"] != -9999)
        & (st.session_state.df_clima["VelocidadedoVento"] != -9999)
        & (st.session_state.df_clima["RadiacaoGlobal"].notna())
        & (st.session_state.df_clima["TemperaturaAr"].notna())
        & (st.session_state.df_clima["VelocidadedoVento"].notna())
        & (st.session_state.df_clima["RadiacaoGlobal"].astype(str) != "")
        & (st.session_state.df_clima["TemperaturaAr"].astype(str) != "")
        & (st.session_state.df_clima["VelocidadedoVento"].astype(str) != "")
    ]
    st.sidebar.dataframe(pd.DataFrame(estacoes, columns=["Estações"]), hide_index=True)
    tabelaminimamaxima = pd.DataFrame(
        [],
        columns=[
            "Estações",
            "Temp. Média Diária",
            "Temp. Máxima Diária",
            "Temp. Minima Diária",
            "Temp. Média das Mínimas",
        ],
    )

    for i in estacoes:
        df = st.session_state.df_clima[st.session_state.df_clima["Estacao"] == i]
        maxima = df["TemperaturaAr"].max()
        media = df["TemperaturaAr"].mean()
        minima = df["TemperaturaAr"].min()
        minimas_diarias = df.groupby(df["Data"])["TemperaturaAr"].min()
        media_minimas_diarias = minimas_diarias.mean()

        tabelaminimamaxima = pd.concat(
            [
                tabelaminimamaxima,
                pd.DataFrame(
                    [
                        {
                            "Estações": i,
                            "Temp. Média Diária": round(media, 2),
                            "Temp. Máxima Diária": round(maxima, 2),
                            "Temp. Minima Diária": round(minima, 2),
                            "Temp. Média das Mínimas": round(media_minimas_diarias, 2),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    st.subheader("")
    st.title("Temperaturas Médias")
    st.dataframe(tabelaminimamaxima, use_container_width=True, hide_index=True)
