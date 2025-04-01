import streamlit as st
from funcoes.buscarbase import BuscarEstacoes, BuscarBaseINMETporEstacoes
import pandas as pd

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

        st.sidebar.table(pd.DataFrame(estacoesclima, columns=["Estações"]))

        if st.button("Aplicar"):

            with st.spinner("Aguarde, estou consultando a Base do INMET..."):

                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)
else:
    estacoesclima = st.multiselect(
        "Selecionar Estações", options=sorted(BuscarEstacoes()["Estacao"])
    )
    if st.session_state.df_clima is None:

        st.sidebar.table(pd.DataFrame(estacoesclima, columns=["Estações"]))

        if st.button("Aplicar"):

            with st.spinner("Aguarde, estou consultando a Base do INMET..."):

                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)
    else:
        if st.button("Atualizar"):
            with st.spinner("Aguarde, estou consultando a Base do INMET..."):
                st.session_state.df_clima = BuscarBaseINMETporEstacoes(estacoesclima)
