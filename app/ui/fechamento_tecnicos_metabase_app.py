import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.metabase_service import carregar_fechamento_metabase
from app.ui.relatorio_financeiro_instalacoes_app import render_relatorio_financeiro_instalacoes


# ======================================================
# COLUNAS PADRÃO DA API
# ======================================================
COL_NUMERO = "numero_ordem_servico"
COL_TECNICO = "usuario_fechamento"
COL_USUARIO_ABERTURA = "usuario_abertura"
COL_TIPO_OS = "tipo_ordem_servico"
COL_DATA_FIM = "data_termino_executado"

TIPOS_OS_FECHAMENTO_POR_CONTA = {
    "amazonet": [
        "AMZ QUALIDADE - NÃO CONFORMIDADES",
        "MUDANÇA DE ENDEREÇO - R$50,00",
        "MUDANÇA DE ENDEREÇO",
        "INSTALAÇÃO (R$ 100,00)",
        "INSTALAÇÃO (R$ 49,90)",
        "INSTALAÇÃO GRÁTIS",
        "INSTALAÇÃO (R$ 50,00)"
    ],
    "mania": [
        "INSTALAÇÃO (R$ 20,00)",
        "MANIA QUALIDADE - NÃO CONFORMIDADES",
        "MUDANÇA DE ENDEREÇO",
        "INSTALAÇÃO WI-FI+ (R$ 20,00)",
        "INSTALAÇÃO (R$ 100,00)",
    ],
}


# ======================================================
# CACHE DE DADOS
# ======================================================
@st.cache_data(ttl=900, show_spinner=False)
def carregar_base(contas, data_inicio, data_fim):
    dfs = []

    for conta in contas:
        df = carregar_fechamento_metabase(conta, data_inicio, data_fim)
        if not df.empty:
            df["conta"] = conta
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs, ignore_index=True)

    # 🔒 GARANTE COLUNAS MESMO SE NÃO VIEREM NA API
    for col in [COL_TECNICO, COL_USUARIO_ABERTURA, COL_DATA_FIM]:
        if col not in df_final.columns:
            df_final[col] = None

    # 📅 Converte datas
    df_final[COL_DATA_FIM] = pd.to_datetime(
        df_final[COL_DATA_FIM],
        format="%d/%m/%Y",
        errors="coerce"
    )

    return df_final


# ======================================================
# APP
# ======================================================
def render_fechamento_metabase():
    st.title("📋 Fechamento Técnico – Metabase")

    st.session_state.setdefault("df_base", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # =========================
    # SIDEBAR
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["amazonet", "mania"],
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início", hoje - timedelta(days=7))
        data_fim = st.date_input("Data fim", hoje)

        gerar = st.button("📊 Gerar relatório")

    # =========================
    # CARREGAMENTO
    # =========================
    if gerar:
        with st.spinner("🔄 Carregando dados do Metabase..."):
            df_base = carregar_base(contas, data_inicio, data_fim)

        if df_base.empty:
            st.warning("Nenhum dado retornado pelo Metabase.")
            return

        # 🔒 FILTRA TIPOS DE OS PERMITIDOS
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
    col1, col2 = st.columns(2)

    # 👷 TÉCNICO
    with col1:
        st.markdown("### 👷 Técnico que fechou")

        busca_tecnico = st.text_input("Buscar técnico")

        tecnicos = sorted(df_base[COL_TECNICO].dropna().astype(str).unique())

        if busca_tecnico:
            tecnicos = [t for t in tecnicos if busca_tecnico.lower() in t.lower()]

        filtro_tecnico = st.multiselect("Selecionar técnico(s)", tecnicos, default=tecnicos)

    # 👤 USUÁRIO ABERTURA
    with col2:
        st.markdown("### 👤 Usuário que abriu")

        usuarios = sorted(df_base[COL_USUARIO_ABERTURA].dropna().astype(str).unique())

        filtro_usuario_abertura = st.multiselect(
            "Selecionar usuário(s)",
            usuarios,
            default=usuarios
        )

    # 🧾 TIPO OS
    tipos_os = sorted(df_base[COL_TIPO_OS].dropna().unique())
    filtro_tipo_os = st.multiselect("Tipos de OS", tipos_os, default=tipos_os)

    # =========================
    # APLICA FILTROS
    # =========================
    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_usuario_abertura:
        df = df[df[COL_USUARIO_ABERTURA].isin(filtro_usuario_abertura)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    st.success(f"✅ {len(df)} ordens encontradas")

    # =========================
    # TABELA FINAL
    # =========================
    colunas_exibir = [
        "numero_ordem_servico",
        "tipo_ordem_servico",
        "usuario_fechamento",
        "usuario_abertura",
        "nome_cliente",
        "codigo_cliente",
        "bairro",
        "cidade",
        "motivo_fechamento",
        "data_cadastro_os",
        "data_termino_executado",
        "conta",
    ]

    colunas_exibir = [c for c in colunas_exibir if c in df.columns]
    df_exibir = df[colunas_exibir].sort_values(COL_DATA_FIM, ascending=False)

    st.dataframe(df_exibir, use_container_width=True, hide_index=True)

    # =====================================
    # DISPONIBILIZA PARA O FINANCEIRO
    # =====================================
    st.session_state["df_fechamento_filtrado"] = df.copy()

    if not df.empty:
        st.markdown("---")
        render_relatorio_financeiro_instalacoes()
