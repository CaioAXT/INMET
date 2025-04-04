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
    listasobrecarga99 = []
    listasobrecarga95 = []
    listanominal99 = []
    listanominal85 = []
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
        listasobrecarga99.append(df_estacao["Tcsobrec"].quantile(0.99))
        listasobrecarga95.append(df_estacao["Tcsobrec"].quantile(0.95))
        listanominal99.append(df_estacao["Tcnom"].quantile(0.99))
        listanominal85.append(df_estacao["Tcnom"].quantile(0.85))
        df_risco = pd.concat([df_risco, df_riscounitario], ignore_index=True)

    df_risco = df_risco.style.set_properties(**{"width": "1000px"})
    st.dataframe(df_risco, hide_index=True, width=1000)
    st.subheader("")
    # endregion

    with st.expander("Mapa Geral"):
        # region Mapa Geral
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

    # region Risco Térmico Gráfico - Sobrec 99%
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
        listaisotocas85nom = []
        listaisotocas99nom = []
        listaisotocas95sob = []
        listaisotocas99sob = []

        for estacao_row in estacoes_filtradas.itertuples():
            latestacaoisotoca = estacao_row.Latitude
            longestacaoisotoca = estacao_row.Longitude

            distancia = 1 / np.sqrt(
                (latestacaoisotoca - latpontointermediario) ** 2
                + (longestacaoisotoca - longpontointermediario) ** 2
            )

            temp85nom = listanominal85[num]
            valorisotoca85 = distancia * temp85nom
            listaisotocas85nom.append(valorisotoca85)

            temp99nom = listanominal99[num]
            valorisotoca99nom = distancia * temp99nom
            listaisotocas99nom.append(valorisotoca99nom)

            temp95sob = listasobrecarga95[num]
            valorisotoca95sob = distancia * temp95sob
            listaisotocas95sob.append(valorisotoca95sob)

            temp99sob = listasobrecarga99[num]
            valorisotoca99sob = distancia * temp99sob
            listaisotocas99sob.append(valorisotoca99sob)

            num += 1

        df_diretriz_filtrada.loc[i, "Temp. Nominal 85%"] = np.mean(listaisotocas85nom)
        df_diretriz_filtrada.loc[i, "Temp. Nominal 99%"] = np.mean(listaisotocas99nom)
        df_diretriz_filtrada.loc[i, "Temp. Sobrecarga 95%"] = np.mean(
            listaisotocas95sob
        )
        df_diretriz_filtrada.loc[i, "Temp. Sobrecarga 99%"] = np.mean(
            listaisotocas99sob
        )
        i += 1

    maiorvalor = max(
        df_diretriz_filtrada["Temp. Nominal 85%"].max(),
        df_diretriz_filtrada["Temp. Nominal 99%"].max(),
        df_diretriz_filtrada["Temp. Sobrecarga 95%"].max(),
        df_diretriz_filtrada["Temp. Sobrecarga 99%"].max(),
    )

    menorvalor = min(
        df_diretriz_filtrada["Temp. Nominal 85%"].min(),
        df_diretriz_filtrada["Temp. Nominal 99%"].min(),
        df_diretriz_filtrada["Temp. Sobrecarga 95%"].min(),
        df_diretriz_filtrada["Temp. Sobrecarga 99%"].min(),
    )
    st.dataframe(df_diretriz_filtrada, hide_index=True)

    with st.expander("Gráficos Nominal"):
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter_mapbox(
                df_diretriz_filtrada,
                lat="Longitude",
                lon="Latitude",
                color="Temp. Nominal 85%",
                height=735,
                center={
                    "lat": df_diretriz_filtrada["Longitude"].mean(),
                    "lon": df_diretriz_filtrada["Latitude"].mean(),
                },
                zoom=7,
                mapbox_style="open-street-map",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                range_color=[menorvalor, maiorvalor],
                hover_data=["Estacao"],
            )
            st.plotly_chart(fig)
        with col2:
            fig = px.scatter_mapbox(
                df_diretriz_filtrada,
                lat="Longitude",
                lon="Latitude",
                color="Temp. Nominal 99%",
                height=735,
                center={
                    "lat": df_diretriz_filtrada["Longitude"].mean(),
                    "lon": df_diretriz_filtrada["Latitude"].mean(),
                },
                zoom=7,
                mapbox_style="open-street-map",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                hover_data=["Estacao"],
                range_color=[menorvalor, maiorvalor],
            )
            st.plotly_chart(fig)

    with st.expander("Gráficos Sobrecarga"):
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter_mapbox(
                df_diretriz_filtrada,
                lat="Longitude",
                lon="Latitude",
                color="Temp. Sobrecarga 95%",
                height=735,
                center={
                    "lat": df_diretriz_filtrada["Longitude"].mean(),
                    "lon": df_diretriz_filtrada["Latitude"].mean(),
                },
                zoom=7,
                mapbox_style="open-street-map",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                hover_data=["Estacao"],
                range_color=[menorvalor, maiorvalor],
            )
            st.plotly_chart(fig)
        with col2:
            fig = px.scatter_mapbox(
                df_diretriz_filtrada,
                lat="Longitude",
                lon="Latitude",
                color="Temp. Sobrecarga 99%",
                height=735,
                center={
                    "lat": df_diretriz_filtrada["Longitude"].mean(),
                    "lon": df_diretriz_filtrada["Latitude"].mean(),
                },
                zoom=7,
                mapbox_style="open-street-map",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                hover_data=["Estacao"],
                range_color=[menorvalor, maiorvalor],
            )
            st.plotly_chart(fig)

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
