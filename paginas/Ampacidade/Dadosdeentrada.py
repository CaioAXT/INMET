import streamlit as st
from funcoes.funcoes import diretriz, haversine, tcnom, parse_to_float
from funcoes.buscarbase import BuscarBaseINMETporEstacoes
import numpy as np
import pandas as pd

estacoesselecionadas = st.session_state.get("estacoesselecionadas", [])

with st.expander("Buffer e Faixa esperada"):

    st.text("")
    colbuffer, colbuffer2 = st.columns([1, 1])
    with colbuffer:
        buffer = st.number_input(
            "Buffer",
            format="%d",
            value=st.session_state.inputs.get("buffer", 0),
            key="buffer",
        )
        st.session_state.inputs["buffer"] = buffer

    with colbuffer2:

        tcnom_min, tcnom_max = st.slider(
            "Defina a faixa esperada da temperatura do condutor",
            min_value=10,
            max_value=250,
            value=(
                st.session_state.inputs.get("tcnom_min", 20),
                st.session_state.inputs.get("tcnom_max", 200),
            ),
            format="%0d",
        )
        st.session_state.inputs["tcnom_min"] = tcnom_min
        st.session_state.inputs["tcnom_max"] = tcnom_max

with st.expander("Informações Gerais"):
    st.text("")
    col_a, col_b = st.columns([1, 1])

    tensao = col_a.number_input(
        "Tensão (kV)",
        format="%d",  # Alterado para inteiro
        value=st.session_state.inputs.get("tensao", 0),
        key="tensao_input",
    )
    st.session_state.inputs["tensao"] = tensao

    diamentrototal = col_a.number_input(
        "Diâmetro Total (m)",
        format="%.5f",
        value=st.session_state.inputs.get("diamentrototal", 0.0),
        key="diamentrototal_input",
    )
    st.session_state.inputs["diamentrototal"] = diamentrototal

    diamentroaluminio = col_a.number_input(
        "Diâmetro Alumínio (m)",
        format="%.5f",
        value=st.session_state.inputs.get("diamentroaluminio", 0.0),
        key="diamentroaluminio_input",
    )
    st.session_state.inputs["diamentroaluminio"] = diamentroaluminio

    coefabsorsolar = col_a.number_input(
        "Coef. Absor. Solar",
        format="%.1f",
        value=st.session_state.inputs.get("coefabsorsolar", 0.0),
        key="coefabsorsolar_input",
    )
    st.session_state.inputs["coefabsorsolar"] = coefabsorsolar

    alturamediadalt = col_a.number_input(
        "Altura Média da LT",
        format="%d",  # Alterado para inteiro
        value=st.session_state.inputs.get("alturamediadalt", 0),
        key="alturamediadalt_input",
    )
    st.session_state.inputs["alturamediadalt"] = alturamediadalt

    condutor = col_b.text_input(
        "Condutor",
        value=st.session_state.inputs.get("condutor", ""),
        key="condutor_input",
    )
    st.session_state.inputs["condutor"] = condutor

    feixe = col_b.number_input(
        "Feixe",
        format="%d",  # Alterado para inteiro
        value=st.session_state.inputs.get("feixe", 0),
        key="feixe_input",
    )
    st.session_state.inputs["feixe"] = feixe

    rdc20cc = col_b.number_input(
        "RDC20º CC(ohms/km)",
        format="%.3f",
        value=st.session_state.inputs.get("rdc20cc", 0.0),
        key="rdc20cc_input",
    )
    st.session_state.inputs["rdc20cc"] = rdc20cc

    epsilon = col_b.number_input(
        "Epsilon",
        format="%.2f",
        value=st.session_state.inputs.get("epsilon", 0.0),
        key="epsilon_input",
    )
    st.session_state.inputs["epsilon"] = epsilon

    coefvarrestemp = col_b.number_input(
        "Coef.Var.Res.Temp °C-¹",
        format="%.5f",
        value=st.session_state.inputs.get("coefvarrestemp", 0.0),
        key="coefvarrestemp_input",
    )
    st.session_state.inputs["coefvarrestemp"] = coefvarrestemp


with st.expander("Correntes de Referência"):
    col_a, col_b = st.columns([1, 1])

    idnom = col_a.number_input(
        "ID-Nom",
        format="%.1f",
        value=st.session_state.inputs.get("idnom", 0.0),
        key="idnom_input",
    )
    st.session_state.inputs["idnom"] = idnom

    innom = col_a.number_input(
        "IN-Nom",
        format="%.1f",
        value=st.session_state.inputs.get("innom", 0.0),
        key="innom_input",
    )
    st.session_state.inputs["innom"] = innom

    vdnom = col_a.number_input(
        "VD-Nom",
        format="%.1f",
        value=st.session_state.inputs.get("vdnom", 0.0),
        key="vdnom_input",
    )
    st.session_state.inputs["vdnom"] = vdnom

    vnnom = col_a.number_input(
        "VN-Nom",
        format="%.1f",
        value=st.session_state.inputs.get("vnnom", 0.0),
        key="vnnom_input",
    )
    st.session_state.inputs["vnnom"] = vnnom

    idsobrec = col_b.number_input(
        "ID-Sobrec",
        format="%.1f",
        value=st.session_state.inputs.get("idsobrec", 0.0),
        key="idsobrec_input",
    )
    st.session_state.inputs["idsobrec"] = idsobrec

    insobrec = col_b.number_input(
        "IN-Sobrec",
        format="%.1f",
        value=st.session_state.inputs.get("insobrec", 0.0),
        key="insobrec_input",
    )
    st.session_state.inputs["insobrec"] = insobrec

    vdsobrec = col_b.number_input(
        "VD-Sobrec",
        format="%.1f",
        value=st.session_state.inputs.get("vdsobrec", 0.0),
        key="vdsobrec_input",
    )
    st.session_state.inputs["vdsobrec"] = vdsobrec

    vnsobrec = col_b.number_input(
        "VN-Sobrec",
        format="%.1f",
        value=st.session_state.inputs.get("vnsobrec", 0.0),
        key="vnsobrec_input",
    )
    st.session_state.inputs["vnsobrec"] = vnsobrec

with st.expander("Vértices da LT"):

    # region VerticesINMET
    COLUNAS_FIXAS = ["Nome do Vertice", "Latitude", "Longitude"]

    st.subheader("Pontos")
    st.text("A ordenação deles é fundamental para a Diretriz da LT no mapa.")

    df = st.session_state.df_pontos_vertices
    df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: f"{x:.6f}".replace(".", ","))
    PontosVertices = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="pontos_vertices_editor",  # Chave única para o editor
    )
    PontosVertices["Latitude"] = (
        PontosVertices["Latitude"].replace(",", ".", regex=True).astype(float)
    )
    PontosVertices["Longitude"] = (
        PontosVertices["Longitude"].replace(",", ".", regex=True).astype(float)
    )

if not PontosVertices.equals(st.session_state.df_pontos_vertices):
    st.session_state.df_pontos_vertices = PontosVertices

aplicarpontosinseridos = st.button("Aplicar")

if st.session_state.df_total is not None:
    st.success(
        "Dados disponíveis nas páginas 'Ver Risco Térmico' e 'Ver intervalos de medição'"
    )

if aplicarpontosinseridos:
    if PontosVertices.isnull().values.any() or not all(
        PontosVertices.iloc[:, 1:].applymap(lambda x: isinstance(x, float)).all(axis=1)
    ):
        st.error(
            "Por favor, preencha todas as informações corretamente. As colunas 'Latitude' e 'Longitude' devem ser números."
        )
    else:
        st.success("Todas as informações foram preenchidas corretamente.")
        with st.spinner("Aguarde, estou consultando a Base do INMET..."):

            PontosDiretriz = diretriz(PontosVertices, 0.1)

            for index, row in PontosDiretriz.iterrows():
                nom = row["Estacao"]
                lat = row["Latitude"]
                long = row["Longitude"]
                for index, row in st.session_state.df_pontos.iterrows():
                    nom_est = row["Estacao"]
                    nom_lat = row["Latitude"]
                    nom_long = row["Longitude"]
                    if (
                        haversine(lat1=lat, lon1=long, lat2=nom_lat, lon2=nom_long)
                        <= buffer
                    ):
                        estacoesselecionadas.append(nom_est)
            estacoesselecionadas = list(set(estacoesselecionadas))

            if estacoesselecionadas:

                df = BuscarBaseINMETporEstacoes(estacoesselecionadas)
                st.text(f"Linhas processadas totais: {format(len(df), ',d')}")

                df = df[
                    (df["RadiacaoGlobal"] != -9999)
                    & (df["TemperaturaAr"] != -9999)
                    & (df["VelocidadedoVento"] != -9999)
                    & (df["RadiacaoGlobal"].notna())
                    & (df["TemperaturaAr"].notna())
                    & (df["VelocidadedoVento"].notna())
                    & (df["RadiacaoGlobal"].astype(str) != "")
                    & (df["TemperaturaAr"].astype(str) != "")
                    & (df["VelocidadedoVento"].astype(str) != "")
                ]

                st.text(f"Linhas processadas válidas: {format(len(df), ',d')}")
            else:
                st.error("Nenhuma estação selecionada")

            df["Tcnom"] = np.vectorize(tcnom)(
                st.session_state.inputs["alturamediadalt"],
                st.session_state.inputs["diamentrototal"],
                st.session_state.inputs["diamentroaluminio"],
                st.session_state.inputs["epsilon"],
                st.session_state.inputs["coefabsorsolar"],
                st.session_state.inputs["coefvarrestemp"],
                st.session_state.inputs["feixe"],
                st.session_state.inputs["rdc20cc"],
                df["TemperaturaAr"].apply(parse_to_float),
                df["RadiacaoGlobal"].apply(parse_to_float),
                df["VelocidadedoVento"].apply(parse_to_float),
                df["Data"].apply(lambda x: int(str(x).replace("-", "/").split("/")[1])),
                df["Hora"].apply(lambda x: int(str(x)[:2])),
                st.session_state.inputs["idnom"],
                st.session_state.inputs["innom"],
                st.session_state.inputs["vdnom"],
                st.session_state.inputs["vnnom"],
                st.session_state.inputs["idsobrec"],
                st.session_state.inputs["insobrec"],
                st.session_state.inputs["vdsobrec"],
                st.session_state.inputs["vnsobrec"],
                True,
                1.0,
                st.session_state.inputs["tcnom_min"],
                st.session_state.inputs["tcnom_max"],
            )

            df["Tcsobrec"] = np.vectorize(tcnom)(
                st.session_state.inputs["alturamediadalt"],
                st.session_state.inputs["diamentrototal"],
                st.session_state.inputs["diamentroaluminio"],
                st.session_state.inputs["epsilon"],
                st.session_state.inputs["coefabsorsolar"],
                st.session_state.inputs["coefvarrestemp"],
                st.session_state.inputs["feixe"],
                st.session_state.inputs["rdc20cc"],
                df["TemperaturaAr"].apply(parse_to_float),
                df["RadiacaoGlobal"].apply(parse_to_float),
                df["VelocidadedoVento"].apply(parse_to_float),
                df["Data"].apply(lambda x: int(str(x).replace("-", "/").split("/")[1])),
                df["Hora"].apply(lambda x: int(str(x)[:2])),
                st.session_state.inputs["idnom"],
                st.session_state.inputs["innom"],
                st.session_state.inputs["vdnom"],
                st.session_state.inputs["vnnom"],
                st.session_state.inputs["idsobrec"],
                st.session_state.inputs["insobrec"],
                st.session_state.inputs["vdsobrec"],
                st.session_state.inputs["vnsobrec"],
                False,
                1.0,
                40,
                250,
            )

            df = df[df["Tcnom"] != 249.99]

            PontosCombinados = pd.concat(
                [
                    st.session_state.df_pontos,
                    PontosDiretriz,
                ],
                ignore_index=True,
            )
            st.session_state.df_diretriz = PontosCombinados
            st.session_state.df_total = df
            st.session_state.df_pontos = estacoesselecionadas

        st.success(
            "Dados disponíveis nas páginas 'Ver Risco Térmico' e 'Ver intervalos de medição'"
        )
