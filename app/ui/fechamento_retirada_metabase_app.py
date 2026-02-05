import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.metabase_service import carregar_fechamento_metabase
from app.analysis.relatorios.fechamento_retirada import relatorio_fechamento_retirada_df
from app.ui.relatorio_financeiro_retirada_app import render_relatorio_financeiro_retirada

# ======================================================
# COLUNAS PADRÃO
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
# FUNÇÕES AUXILIARES
# ======================================================
def garantir_colunas(df: pd.DataFrame) -> pd.DataFrame:
    colunas_necessarias = [
        COL_NUMERO, COL_TECNICO, COL_TIPO_OS, COL_DATA_FIM,
        "nome_cliente", "cidade", "bairro", "codigo_cliente",
        "motivo_fechamento", "conta"
    ]
    for col in colunas_necessarias:
        if col not in df.columns:
            df[col] = None
    return df


def normalizar_datas(df: pd.DataFrame) -> pd.DataFrame:
    if COL_DATA_FIM in df.columns:
        df[COL_DATA_FIM] = pd.to_datetime(
            df[COL_DATA_FIM], dayfirst=True, errors="coerce"
        )
    return df


# ======================================================
# CACHE METABASE
# ======================================================
@st.cache_data(ttl=900, show_spinner=False)
def carregar_base(contas, data_inicio, data_fim) -> pd.DataFrame:
    dfs = []

    for conta in contas:
        # 🔽 BUSCA DIRETO DO METABASE
        df_metabase = carregar_fechamento_metabase(conta, data_inicio, data_fim)

        if df_metabase is None or df_metabase.empty:
            continue

        # 🔽 TRATAMENTO (SEM HUBSOFT)
        df_tratado = relatorio_fechamento_retirada_df(df_metabase)

        if df_tratado.empty:
            continue

        df_tratado["conta"] = conta
        dfs.append(df_tratado)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs, ignore_index=True)
    df_final = garantir_colunas(df_final)
    df_final = normalizar_datas(df_final)

    return df_final


# ======================================================
# APP
# ======================================================
def render_retirada_metabase():
    st.title("📋 Fechamento Técnico – Retiradas (Metabase)")

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
        st.session_state.setdefault("df_fechamento_filtrado", pd.DataFrame())

    # =========================
    # CARREGAMENTO
    # =========================
    if gerar:
        with st.spinner("🔄 Buscando dados no Metabase..."):
            df_base = carregar_base(contas, data_inicio, data_fim)

        if df_base.empty:
            st.warning("Nenhuma retirada encontrada no período.")
            return

        # 🔒 Filtra tipos de OS válidos por conta
        tipos_permitidos = set()
        for conta in contas:
            tipos_permitidos.update(TIPOS_OS_FECHAMENTO_POR_CONTA.get(conta, []))

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

    col1, col2, col3 = st.columns(3)

    with col1:
        busca = st.text_input("Buscar técnico")

        tecnicos = sorted(
            df_base[COL_TECNICO].dropna().astype(str).unique()
        )

        if busca:
            tecnicos = [t for t in tecnicos if busca.lower() in t.lower()]

        filtro_tecnico = st.multiselect("Técnico", tecnicos, default=tecnicos)

    with col2:
        tipos_os = sorted(df_base[COL_TIPO_OS].dropna().unique())
        filtro_tipo_os = st.multiselect("Tipo OS", tipos_os, default=tipos_os)

    with col3:
        tipos_fechamento = sorted(df_base["motivo_fechamento"].dropna().unique())
        filtro_tipo_fechamento = st.multiselect(
            "motivo_fechamento",
            tipos_fechamento,
            default=tipos_fechamento
        )

    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    if filtro_tipo_fechamento:
        df = df[df["motivo_fechamento"].isin(filtro_tipo_fechamento)]



    # =========================
    # TABELA
    # =========================
    st.dataframe(
        df.sort_values(COL_DATA_FIM, ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # =====================================
    # ENVIA PARA O FINANCEIRO
    # =====================================
    st.session_state["df_fechamento_filtrado"] = df

    if not df.empty:
        st.markdown("---")
        render_relatorio_financeiro_retirada()
