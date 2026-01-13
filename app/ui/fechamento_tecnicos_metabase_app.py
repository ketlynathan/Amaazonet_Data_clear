import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.services.metabase_service import carregar_fechamento_metabase
from app.ui.relatorio_financeiro_instalacoes_app import render_relatorio_financeiro_instalacoes

# ======================================================
# COLUNAS REAIS (JSON CONFIRMADO)
# ======================================================
COL_NUMERO = "numero_ordem_servico"
COL_TECNICO = "usuario_fechamento"
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
# CACHE
# ======================================================
@st.cache_data(ttl=900, show_spinner=False)
def carregar_base(contas, data_inicio, data_fim):
    dfs = []

    for conta in contas:
        df = carregar_fechamento_metabase(conta, data_inicio, data_fim)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)

# ======================================================
# APP
# ======================================================
def render_fechamento_metabase():
    st.title("📋 Fechamento Técnico – Metabase")

    # =========================
    # SESSION STATE
    # =========================
    st.session_state.setdefault("df_base", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # =========================
    # SIDEBAR
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros base") 
        contas = st.multiselect( 
            "Contas", ["mania", "amazonet"], 
            default=["amazonet", "mania"], )

        hoje = date.today() 
        data_inicio = st.date_input( 
            "Data início", 
            hoje - timedelta(days=7), 
            ) 
        data_fim = st.date_input(
             "Data fim", hoje, 
             ) 
        gerar = st.button("📊 Gerar relatório") 
        
        if "df_fechamento_filtrado" not in st.session_state: st.session_state["df_fechamento_filtrado"] = pd.DataFrame()



    # =========================
    # CARREGAMENTO (SÓ NO BOTÃO)
    # =========================
    if gerar:
        with st.spinner("🔄 Carregando dados do Metabase..."):
            df_base = carregar_base(contas, data_inicio, data_fim)

        if df_base.empty:
            st.warning("Nenhum dado retornado pelo Metabase.")
            return

        # 🔒 FILTRA TIPOS PERMITIDOS POR CONTA
        tipos_permitidos = set()
        for conta in contas:
            tipos_permitidos.update(
                TIPOS_OS_FECHAMENTO_POR_CONTA[conta]
            )

        df_base = df_base[
            df_base[COL_TIPO_OS].isin(tipos_permitidos)
        ]

        st.session_state["df_base"] = df_base
        st.session_state["carregado"] = True

    if not st.session_state["carregado"]:
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

    # =========================
    # FILTROS PÓS-CARGA
    # =========================
    st.subheader("🎯 Filtros")

    col1, col2 = st.columns(2)

    # ----------- TÉCNICO -----------
    with col1:
        st.markdown("### 👷 Técnico")

        busca = st.text_input(
            "Buscar técnico",
            placeholder="Ex: Lobatos, Silva, Moura",
        )

        tecnicos = (
            df_base[COL_TECNICO]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        tecnicos.sort()

        if busca:
            tecnicos = [
                t for t in tecnicos if busca.lower() in t.lower()
            ]

        filtro_tecnico = st.multiselect(
            "Selecionar técnico(s)",
            tecnicos,
            default=tecnicos,
        )

    # ----------- TIPO OS -----------
    with col2:
        st.markdown("### 🧾 Tipo de Ordem de Serviço")

        tipos_os = sorted(
            df_base[COL_TIPO_OS].dropna().unique().tolist()
        )

        filtro_tipo_os = st.multiselect(
            "Tipos de OS",
            tipos_os,
            default=tipos_os,
        )

    # =========================
    # APLICA FILTROS
    # =========================
    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    st.success(f"✅ {len(df)} ordens encontradas")

    # =========================
    # TABELA
    # =========================
    colunas_exibir = [
        "numero_ordem_servico",
        "tipo_ordem_servico",
        "usuario_fechamento",
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

    df_exibir = df[colunas_exibir]

    if COL_DATA_FIM in df_exibir.columns:
        df_exibir = df_exibir.sort_values(
            COL_DATA_FIM, ascending=False
        )

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================
    # DF FINAL (APÓS TODOS OS FILTROS)
    # =====================================
    df_final = df.copy()

    # 🔗 DISPONIBILIZA PARA O FINANCEIRO
    st.session_state["df_fechamento_filtrado"] = df_final

    if not df_final.empty:
        st.markdown("---")
        st.header("💰 Relatório Financeiro")
        render_relatorio_financeiro_instalacoes()

