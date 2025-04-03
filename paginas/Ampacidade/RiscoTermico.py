import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

if st.session_state.df_total is None:
    st.warning("Nenhum dado processado disponível, preencha a aba 'Dados de Entrada'")
else:
    st.session_state.df_diretriz.loc[
        st.session_state.df_diretriz["Estacao"].isin(st.session_state.df_pontos),
        "Classificação do Ponto",
    ] = "Dentro do Buffer"

    # region Risco Térmico Numérico
    st.subheader("")
    df_risco = pd.DataFrame(
        columns=[
            "Estacao",
            "Tcnom_85 (em ºC)",
            "Tcnom_99 (em ºC)",
            "Tcsobrec_95 (em ºC)",
            "Tcsobrec_99 (em ºC)",
        ]
    )
    listasobrecarga = []
    for estacao in sorted(st.session_state.df_pontos):
        df_estacao = st.session_state.df_total[
            st.session_state.df_total["Estacao"] == estacao
        ]
        df_estacao = df_estacao[
            (df_estacao["Tcnom"] != 249.99) & (df_estacao["Tcsobrec"] != 249.99)
        ]

        df_riscounitario = pd.DataFrame(
            {
                "Estacao": [estacao],
                "Tcnom_85 (em ºC)": [
                    str(round(df_estacao["Tcnom"].quantile(0.85), 2)).replace(".", ",")
                ],
                "Tcnom_99 (em ºC)": [
                    str(round(df_estacao["Tcnom"].quantile(0.99), 2)).replace(".", ",")
                ],
                "Tcsobrec_95 (em ºC)": [
                    str(round(df_estacao["Tcsobrec"].quantile(0.95), 2)).replace(
                        ".", ","
                    )
                ],
                "Tcsobrec_99 (em ºC)": [
                    str(round(df_estacao["Tcsobrec"].quantile(0.99), 2)).replace(
                        ".", ","
                    )
                ],
            }
        )
        listasobrecarga.append(df_estacao["Tcsobrec"].quantile(0.99))
        df_risco = pd.concat([df_risco, df_riscounitario], ignore_index=True)

    df_risco = df_risco.style.set_properties(**{"width": "1000px"})
    st.dataframe(df_risco, hide_index=True, width=1000)
    st.subheader("")
    # endregion

    col1, col2 = st.columns(2)
    with col1:
        # region Mapa
        fig = px.scatter_mapbox(
            st.session_state.df_diretriz,
            lat="Longitude",
            lon="Latitude",
            hover_name="Estacao",
            zoom=6,
            color="Classificação do Ponto",
            center={
                "lat": st.session_state.df_diretriz["Longitude"].mean(),
                "lon": st.session_state.df_diretriz["Latitude"].mean(),
            },
            height=600,
            size_max=2,
        )

        fig.update_traces(marker=dict(size=10))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.subheader("")
        st.plotly_chart(fig)
        # endregion

    with col2:
        # region Risco Térmico Gráfico
        df_diretriz_filtrada = st.session_state.df_diretriz[
            st.session_state.df_diretriz["Classificação do Ponto"] != "Dentro do Buffer"
        ]
        estacoes_filtradas = st.session_state.df_diretriz[
            st.session_state.df_diretriz["Classificação do Ponto"] == "Dentro do Buffer"
        ]

        i = 0

        for row in df_diretriz_filtrada.itertuples():
            pontointermediario = row.Estacao
            latpontointermediario = row.Latitude
            longpontointermediario = row.Longitude
            num = 0
            listaisotocas = []
            for estacao_row in estacoes_filtradas.itertuples():
                estacaoisotoca = estacao_row.Estacao
                latestacaoisotoca = estacao_row.Latitude
                longestacaoisotoca = estacao_row.Longitude
                temp = listasobrecarga[num]
                valorisotoca = (
                    1
                    / np.sqrt(
                        (latestacaoisotoca - latpontointermediario) ** 2
                        + (longestacaoisotoca - longpontointermediario) ** 2
                    )
                ) * temp
                num += 1
                listaisotocas.append(valorisotoca)
            df_diretriz_filtrada.loc[i, "Temp. Sobrecarga"] = np.mean(listaisotocas)
            i += 1
        fig = px.density_mapbox(
            df_diretriz_filtrada,
            lat="Longitude",
            lon="Latitude",
            z="Temp. Sobrecarga",
            radius=10,
            height=735,
            center={
                "lat": df_diretriz_filtrada["Longitude"].mean(),
                "lon": df_diretriz_filtrada["Latitude"].mean(),
            },
            zoom=7,
            mapbox_style="open-street-map",
            color_continuous_scale=px.colors.sequential.YlOrRd,
            hover_data=["Estacao"],
        )
        st.plotly_chart(fig)
        # endregion

    # region Base de Dados
    st.title("Base de Dados")
    st.subheader("")
    st.dataframe(st.session_state.df_total, hide_index=True)

    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(st.session_state.df_total)

    st.download_button(
        label="Baixar Base de Dados",
        data=csv,
        file_name="base_de_dados.csv",
        mime="text/csv",
    )
    st.sidebar.subheader("Estações dentro do Buffer")
    st.sidebar.table(pd.DataFrame(st.session_state.df_pontos, columns=["Nomes"]))
    # endregion
