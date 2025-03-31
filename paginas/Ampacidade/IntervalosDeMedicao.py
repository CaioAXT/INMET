import streamlit as st
import pandas as pd
import plotly.express as px

if st.session_state.df_total is None:
    st.warning("Nenhum dado processado disponível, preencha a aba 'Dados de Entrada'")
else:
    st.text("")

    estacao_selecionada = st.multiselect(
        "Escolha as Estações",
        sorted(st.session_state.df_pontos),
    )
    anos = sorted(
        st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4])).unique()
    )
    ano_min, ano_max = st.slider(
        "Escolha o Intervalo de Anos",
        min_value=min(anos),
        max_value=max(anos),
        value=(min(anos), max(anos)),
    )
    anos_selecionados = list(range(ano_min, ano_max + 1))

    df_estacao = st.session_state.df_total[
        (st.session_state.df_total["Estacao"].isin(estacao_selecionada))
        & (
            st.session_state.df_total["Data"]
            .apply(lambda x: int(str(x)[:4]))
            .isin(anos_selecionados)
        )
    ]

    for estacao in sorted(estacao_selecionada):
        st.text("")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "TcNom e TcSobrec",
                "Curva Acumulada",
                "Temperatura do Ar",
                "Velocidade do Vento",
                "Radiação Global",
            ]
        )
        with tab1:
            df_estacao = st.session_state.df_total[
                (st.session_state.df_total["Estacao"] == estacao)
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    >= ano_min
                )
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    <= ano_max
                )
            ]

            bins = range(
                st.session_state.inputs["tcnom_min"],
                st.session_state.inputs["tcnom_max"],
                5,
            )
            labels = [f"{i}-{i+5}" for i in bins[:-1]]

            df_estacao["Intervalo_Tcnom"] = pd.cut(
                df_estacao["Tcnom"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_estacao["Intervalo_Tcsobrec"] = pd.cut(
                df_estacao["Tcsobrec"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped_tcnom = (
                df_estacao.groupby("Intervalo_Tcnom", observed=True)
                .size()
                .reset_index(name="Count_Tcnom")
            )

            df_grouped_tcsobrec = (
                df_estacao.groupby("Intervalo_Tcsobrec", observed=True)
                .size()
                .reset_index(name="Count_Tcsobrec")
            )

            df_grouped_tcnom["Percentage_Tcnom"] = (
                df_grouped_tcnom["Count_Tcnom"]
                / df_grouped_tcnom["Count_Tcnom"].sum()
                * 100
            )

            df_grouped_tcsobrec["Percentage_Tcsobrec"] = (
                df_grouped_tcsobrec["Count_Tcsobrec"]
                / df_grouped_tcsobrec["Count_Tcsobrec"].sum()
                * 100
            )
            df_grouped_tcnom = df_grouped_tcnom.rename(
                columns={
                    "Intervalo_Tcnom": "Intervalo",
                    "Percentage_Tcnom": "Percentage",
                }
            )
            df_grouped_tcsobrec = df_grouped_tcsobrec.rename(
                columns={
                    "Intervalo_Tcsobrec": "Intervalo",
                    "Percentage_Tcsobrec": "Percentage",
                }
            )

            df_grouped_tcnom["Tipo"] = "Tcnom"
            df_grouped_tcsobrec["Tipo"] = "Tcsobrec"

            # Concatena
            df_plot = pd.concat(
                [df_grouped_tcnom, df_grouped_tcsobrec], ignore_index=True
            )

            fig = px.bar(
                df_plot,
                x="Intervalo",
                y="Percentage",
                color="Tipo",  # Diferencia Tcnom e Tcsobrec
                barmode="group",  # Lado a lado
                title=f"Estação: {estacao}",
                labels={
                    "Intervalo": "Intervalo (ºC)",
                    "Percentage": "Percentual (%)",
                },
                category_orders={"Intervalo": labels},
                color_discrete_map={"Tcnom": "orange", "Tcsobrec": "red"},
                height=600,
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            df_estacao = st.session_state.df_total[
                (st.session_state.df_total["Estacao"] == estacao)
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    >= ano_min
                )
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    <= ano_max
                )
            ]

            bins = range(
                st.session_state.inputs["tcnom_min"],
                st.session_state.inputs["tcnom_max"],
                5,
            )
            labels = [f"{i}-{i+5}" for i in bins[:-1]]

            df_estacao["Intervalo"] = pd.cut(
                df_estacao["Tcnom"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped_tcnom = (
                df_estacao.groupby("Intervalo", observed=True)
                .size()
                .reset_index(name="Count")
            )

            df_grouped_tcnom["Percentage"] = (
                df_grouped_tcnom["Count"] / df_grouped_tcnom["Count"].sum() * 100
            )

            df_grouped_tcnom["Cumulative Percentage"] = (
                100 - df_grouped_tcnom["Percentage"].cumsum()
            )

            # --------------------------------------------------
            # 2) Agrupar Tcsobrec (mesma lógica, mas com outra coluna)
            # --------------------------------------------------
            df_estacao["Intervalo_tcsobrec"] = pd.cut(
                df_estacao["Tcsobrec"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped_tcsobrec = (
                df_estacao.groupby("Intervalo_tcsobrec", observed=True)
                .size()
                .reset_index(name="Count")
            )

            df_grouped_tcsobrec["Percentage"] = (
                df_grouped_tcsobrec["Count"] / df_grouped_tcsobrec["Count"].sum() * 100
            )

            df_grouped_tcsobrec["Cumulative Percentage"] = (
                100 - df_grouped_tcsobrec["Percentage"].cumsum()
            )

            fig_cumulative = px.line(
                df_grouped_tcnom,
                x="Intervalo",
                y="Cumulative Percentage",
                title=f"Estação: {estacao}",
                labels={
                    "Intervalo": "Intervalo TcNom (ºC)",
                    "Cumulative Percentage": "Percentual Acumulado (%)",
                },
                category_orders={"Intervalo": labels},
                height=600,
                color_discrete_sequence=["orange"],
            )

            fig_cumulative.add_scatter(
                x=df_grouped_tcsobrec["Intervalo_tcsobrec"],
                y=df_grouped_tcsobrec["Cumulative Percentage"],
                mode="lines",
                name="Tcsobrec",
                line=dict(color="red"),
            )

            fig_cumulative.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_cumulative)

        with tab3:
            df_estacao = st.session_state.df_total[
                (st.session_state.df_total["Estacao"] == estacao)
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    >= ano_min
                )
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    <= ano_max
                )
            ]

            bins = range(
                0,
                40,
                2,
            )
            labels = [f"{i}-{i+5}" for i in bins[:-1]]

            df_estacao["TemperaturaAr"] = (
                df_estacao["TemperaturaAr"].replace(",", ".", regex=True).astype(float)
            )

            df_estacao["Intervalo"] = pd.cut(
                df_estacao["TemperaturaAr"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped = (
                df_estacao.groupby("Intervalo", observed=True)
                .size()
                .reset_index(name="Count")
            )

            df_grouped["Percentage"] = (
                df_grouped["Count"] / df_grouped["Count"].sum() * 100
            )

            fig = px.bar(
                df_grouped,
                x="Intervalo",
                y="Percentage",
                title=f"Estação: {estacao}",
                labels={
                    "Intervalo": "Intervalo Temperatura do Ar (ºC)",
                    "Percentage": "Percentual (%)",
                },
                category_orders={"Intervalo": labels},
                height=600,
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)

        with tab4:
            df_estacao = st.session_state.df_total[
                (st.session_state.df_total["Estacao"] == estacao)
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    >= ano_min
                )
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    <= ano_max
                )
            ]

            bins = range(
                0,
                20,
                1,
            )
            labels = [f"{i} - {i+1}" for i in bins[:-1]]

            df_estacao["VelocidadedoVento"] = (
                df_estacao["VelocidadedoVento"]
                .replace(",", ".", regex=True)
                .astype(float)
            )

            df_estacao["Intervalo"] = pd.cut(
                df_estacao["VelocidadedoVento"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped = (
                df_estacao.groupby("Intervalo", observed=True)
                .size()
                .reset_index(name="Count")
            )

            df_grouped["Percentage"] = (
                df_grouped["Count"] / df_grouped["Count"].sum() * 100
            )

            fig = px.bar(
                df_grouped,
                x="Intervalo",
                y="Percentage",
                title=f"Estação: {estacao}",
                labels={
                    "Intervalo": "Intervalo Velocidade do Vento (m/s)",
                    "Percentage": "Percentual (%)",
                },
                category_orders={"Intervalo": labels},
                height=600,
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)

        with tab5:
            df_estacao = st.session_state.df_total[
                (st.session_state.df_total["Estacao"] == estacao)
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    >= ano_min
                )
                & (
                    st.session_state.df_total["Data"].apply(lambda x: int(str(x)[:4]))
                    <= ano_max
                )
            ]

            bins = range(
                0,
                4000,
                100,
            )
            labels = [f"{i} - {i+100}" for i in bins[:-1]]

            df_estacao["RadiacaGlobal"] = (
                df_estacao["RadiacaoGlobal"].replace(",", ".", regex=True).astype(float)
            )

            df_estacao["Intervalo"] = pd.cut(
                df_estacao["RadiacaGlobal"],
                bins=bins,
                labels=labels,
                include_lowest=True,
                right=False,
            )

            df_grouped = (
                df_estacao.groupby("Intervalo", observed=True)
                .size()
                .reset_index(name="Count")
            )

            df_grouped["Percentage"] = (
                df_grouped["Count"] / df_grouped["Count"].sum() * 100
            )

            fig = px.bar(
                df_grouped,
                x="Intervalo",
                y="Percentage",
                title=f"Estação: {estacao}",
                labels={
                    "Intervalo": "Intervalo Radiação Global (W/m2)",
                    "Percentage": "Percentual (%)",
                },
                category_orders={"Intervalo": labels},
                height=600,
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
