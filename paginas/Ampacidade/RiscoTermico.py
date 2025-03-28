import streamlit as st
import pandas as pd
import plotly.express as px

if st.session_state.df_total is None:
    st.warning("Nenhum dado processado disponível, preencha a aba 'Dados de Entrada'")
else:
    st.session_state.df_diretriz.loc[
        st.session_state.df_diretriz["Estacao"].isin(st.session_state.df_pontos),
        "Classificação do Ponto",
    ] = "Dentro do Buffer"

    fig = px.scatter_mapbox(
        st.session_state.df_diretriz,
        lat="Latitude",
        lon="Longitude",
        hover_name="Estacao",
        zoom=3,
        color="Classificação do Ponto",
        center={
            "lat": st.session_state.df_diretriz["Latitude"].mean(),
            "lon": st.session_state.df_diretriz["Longitude"].mean(),
        },
        height=600,
        size_max=2,
    )

    fig.update_traces(marker=dict(size=10))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)

    st.subheader("")

    st.title("Risco Térmico")

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

        df_risco = pd.concat([df_risco, df_riscounitario], ignore_index=True)

    df_risco = df_risco.style.set_properties(**{"width": "1000px"})
    st.dataframe(df_risco, width=1000)
    st.subheader("")
    st.title("Base de Dados")
    st.subheader("")
    st.dataframe(st.session_state.df_total)

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
