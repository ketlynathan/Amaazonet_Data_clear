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

    st.markdown("## 👤 Vendedores Autônomos (51 STM + 60)")

    base_autonomos = resultados["autonomos"]

    tipos = sorted(base_autonomos["tipo_vendedor"].unique())
    tipo_escolhido = st.selectbox("Filtrar tipo de vendedor", tipos)

    filtrado = base_autonomos[base_autonomos["tipo_vendedor"] == tipo_escolhido]

    st.dataframe(filtrado, use_container_width=True)

