import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.google_sheets import read_sheet_as_dataframe
from app.analysis.relatorios.fechamento_retirada import relatorio_fechamento_retirada_df
from app.ui.relatorio_financeiro_retirada_app import render_relatorio_financeiro_retirada
from app.analysis.Financeiro.financeiro_rules_retirada import aplicar_regras_financeiras, carregar_planilha_39
# ======================================================
# COLUNAS REAIS (JSON CONFIRMADO)
# ======================================================
COL_NUMERO = "numero_ordem_servico"
COL_TECNICO = "usuario_fechamento"
COL_TIPO_OS = "tipo_ordem_servico"
COL_DATA_FIM = "data_termino_executado"

TIPOS_OS_FECHAMENTO_POR_CONTA = {
    "amazonet": ["RETIRADA DE EQUIPAMENTOS"],
    "mania": ["RETIRADA DE EQUIPAMENTOS"],
}

# ======================================================
# CACHE
# ======================================================
# ou o nome real da sua função que já buscava no Metabase

@st.cache_data(ttl=900, show_spinner=False)
def carregar_base(contas, data_inicio, data_fim) -> pd.DataFrame:
    dfs = []

    for conta in contas:
        df = relatorio_fechamento_retirada_df(conta, data_inicio, data_fim)
        if df is not None and not df.empty:
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


# ======================================================
# APP
# ======================================================
def render_retirada_metabase():
    st.title("📋 Fechamento Técnico – Metabase")

    st.session_state.setdefault("df_base", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # =========================
    # SIDEBAR
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas", ["mania", "amazonet"],
            default=["amazonet", "mania"]
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início", hoje - timedelta(days=7))
        data_fim = st.date_input("Data fim", hoje)

        gerar = st.button("📊 Gerar relatório")

        if "df_fechamento_filtrado" not in st.session_state:
            st.session_state["df_fechamento_filtrado"] = pd.DataFrame()

    # =========================
    # CARREGAMENTO
    # =========================
    if gerar:
        with st.spinner("🔄 Carregando dados do Metabase..."):
            df_base = carregar_base(contas, data_inicio, data_fim)

        if df_base.empty:
            st.warning("Nenhum dado retornado pelo Metabase.")
            return

        tipos_permitidos = set()
        for conta in contas:
            tipos_permitidos.update(TIPOS_OS_FECHAMENTO_POR_CONTA[conta])

        df_base = df_base[df_base[COL_TIPO_OS].isin(tipos_permitidos)]

        st.session_state["df_base"] = df_base
        st.session_state["carregado"] = True

    if not st.session_state["carregado"]:
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

    # =========================
    # FILTROS
    # =========================
    st.subheader("🎯 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        busca = st.text_input("Buscar técnico")
        tecnicos = sorted(df_base[COL_TECNICO].dropna().astype(str).unique())

        if busca:
            tecnicos = [t for t in tecnicos if busca.lower() in t.lower()]

        filtro_tecnico = st.multiselect("Técnico", tecnicos, default=tecnicos)

    with col2:
        tipos_os = sorted(df_base[COL_TIPO_OS].dropna().unique())
        filtro_tipo_os = st.multiselect("Tipo OS", tipos_os, default=tipos_os)

    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    st.success(f"✅ {len(df)} ordens encontradas")


    # =========================
    # TABELA
    # =========================
    st.dataframe(df, use_container_width=True, hide_index=True)

    # =====================================
    # ENVIA PARA O FINANCEIRO
    # =====================================
    st.session_state["df_fechamento_filtrado"] = df

    if not df.empty:
        st.markdown("---")
        render_relatorio_financeiro_retirada()
