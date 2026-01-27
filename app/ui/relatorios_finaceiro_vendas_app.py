import streamlit as st
import pandas as pd
from datetime import date, timedelta
import app
from app.analysis.metabase_service import carregar_fila_metabase
from app.analysis.Financeiro.financeiro_rules_venda import aplicar_regras


def render_relatorio_financeiro_vendas():
    st.markdown("## 🧾 Resumo Financeiro – Vendas")

    if "df_fechamento_filtrado" not in st.session_state:
        st.warning("Carregue o fechamento primeiro.")
        return

    df_base = st.session_state["df_fechamento_filtrado"].copy()

    if df_base.empty:
        st.warning("Nenhum dado disponível.")
        return

    resultados = aplicar_regras(df_base)

    st.markdown("## 📦 Base Metabase")
    st.dataframe(resultados["base"], use_container_width=True)

    st.markdown("## 🟢 Resultado – Planilha 51 STM")
    st.dataframe(resultados["51_STM"], use_container_width=True)

    st.markdown("## 🔵 Resultado – Planilha 51")
    st.dataframe(resultados["51"], use_container_width=True)

    st.markdown("## 🟠 Resultado – Planilha 60")
    st.dataframe(resultados["60"], use_container_width=True)

    st.markdown("## 📊 Resumo Final")
    st.dataframe(resultados["resumo"], use_container_width=True)
