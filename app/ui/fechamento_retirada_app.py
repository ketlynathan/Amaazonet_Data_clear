import streamlit as st
import pandas as pd
from datetime import date, timedelta


from app.analysis.relatorios.fechamento_retirada import relatorio_fechamento_retirada_df
from app.ui.relatorio_financeiro_retirada_app import render_relatorio_financeiro_retirada                  
# ======================================================
# CONSTANTES
# ======================================================
COL_TECNICO = "usuario_fechamento.name"
COL_TIPO_OS = "tipo_ordem_servico.descricao"
COL_CLIENTE = "dados_cliente.codigo_cliente"
COL_ESTADO = "dados_endereco_instalacao.estado"
COL_SERVICO_STATUS = "dados_servico.servico_status"

TIPOS_OS_FECHAMENTO_POR_CONTA = {
    "amazonet": ["RETIRADA DE EQUIPAMENTOS"],
    "mania": ["RETIRADA DE EQUIPAMENTOS"],
}

# ======================================================
# CACHE – CARGA ÚNICA DA API
# ======================================================
@st.cache_data(ttl=900)
def carregar_df_base(contas, data_inicio, data_fim, estados):
    return relatorio_fechamento_retirada_df(
        contas=contas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        estados=estados,
    )

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def obter_tipos_validos_por_conta(df: pd.DataFrame) -> list[str]:
    tipos = set()

    if "conta" not in df.columns:
        return []

    for conta in df["conta"].dropna().str.lower().unique():
        tipos.update(TIPOS_OS_FECHAMENTO_POR_CONTA.get(conta, []))

    return sorted(tipos)

# ======================================================
# APP
# ======================================================
def render_retirada():
    st.title("📦 Relatório de Retirada")

    # =========================
    # SESSION STATE
    # =========================
    st.session_state.setdefault("df_base", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # =========================
    # SIDEBAR – FILTROS BASE
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas",
            ["amazonet", "mania"],
            default=["amazonet"],
        )

        hoje = date.today()

        data_inicio = st.date_input(
            "Data início",
            value=hoje - timedelta(days=7),
        )

        data_fim = st.date_input(
            "Data fim",
            value=hoje,
        )

        estados = st.multiselect(
            "Estados",
            ["AM", "PA"],
            default=["AM", "PA"],
        )

        gerar = st.button("📊 Gerar relatório")

    # =========================
    # CARGA DA API
    # =========================
    if gerar:
        if not contas:
            st.error("Selecione ao menos uma conta.")
            return

        if data_inicio > data_fim:
            st.error("Data início maior que data fim.")
            return

        with st.spinner("🔄 Carregando ordens de serviço..."):
            df = carregar_df_base(
                contas,
                data_inicio,
                data_fim,
                estados,
            )

        if df.empty:
            st.warning("Nenhuma ordem encontrada.")
            return

        st.session_state["df_base"] = df.copy()
        st.session_state["carregado"] = True

    if not st.session_state["carregado"]:
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

    # ======================================================
    # FILTROS PÓS-CARGA
    # ======================================================
    st.subheader("🎯 Filtros")

    col1, col2 = st.columns(2)

    # -------- TÉCNICO --------
    with col1:
        busca_tecnico = st.text_input(
            "🔍 Buscar técnico",
            placeholder="Ex: Wadison, Oliveira",
            key="busca_tecnico_retirada",
        )

        tecnicos = (
            df_base[COL_TECNICO]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        tecnicos.sort()

        if busca_tecnico:
            tecnicos = [
                t for t in tecnicos
                if busca_tecnico.lower() in t.lower()
            ]

        filtro_tecnico = st.multiselect(
            "👷 Técnico",
            tecnicos,
            default=tecnicos,
        )

    # -------- TIPO OS --------
    with col2:
        tipos_validos = obter_tipos_validos_por_conta(df_base)

        filtro_tipo_os = st.multiselect(
            "🧾 Tipo de OS",
            tipos_validos,
            default=tipos_validos,
        )

    # =========================
    # APLICA FILTROS
    # =========================
    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    if df.empty:
        st.warning("Nenhum registro após aplicar os filtros.")
        return

    # ======================================================
    # ALERTAS E VALIDAÇÕES
    # ======================================================

    # -------- ALERTA SERVIÇO HABILITADO --------
    df["alerta_servico"] = df[COL_SERVICO_STATUS].apply(
        lambda x: "⚠️ Serviço Habilitado"
        if str(x).upper() == "SERVIÇO HABILITADO"
        else ""
    )

    # -------- CLIENTE DUPLICADO --------
    duplicados = (
        df[COL_CLIENTE]
        .value_counts()
        .loc[lambda x: x > 1]
    )

    if not duplicados.empty:
        st.warning(
            f"⚠️ Existem {len(duplicados)} clientes duplicados no período."
        )

    st.success(f"✅ {len(df)} ordens válidas para fechamento")

    # ======================================================
    # TABELA
    # ======================================================
    colunas_exibir = [
        "numero",
        COL_TIPO_OS,
        COL_TECNICO,
        COL_CLIENTE,
        "dados_cliente.nome_razaosocial",
        "dados_endereco_instalacao.cidade",
        COL_ESTADO,
        "conta",
        "status",
        "data_termino_executado",
        COL_SERVICO_STATUS,
        "alerta_servico",
    ]

    colunas_exibir = [c for c in colunas_exibir if c in df.columns]

    st.dataframe(
        df[colunas_exibir],
        use_container_width=True,
        hide_index=True,
    )

    # ======================================================
    # PREPARA PARA FINANCEIRO
    # ======================================================
    df_fin = df.rename(columns={
        COL_CLIENTE: "codigo_cliente",
        "numero": "numero_ordem_servico",
        COL_TECNICO: "usuario_fechamento",
    })

    colunas_obrigatorias = {
        "codigo_cliente",
        "numero_ordem_servico",
        "usuario_fechamento",
    }

    faltando = colunas_obrigatorias - set(df_fin.columns)
    if faltando:
        st.error(f"Colunas obrigatórias ausentes: {faltando}")
        return

    st.session_state["df_fechamento_filtrado"] = df_fin

    # ======================================================
    # FINANCEIRO
    # ======================================================
    if not df_fin.empty:
        st.markdown("---")
        st.header("💰 Relatório Financeiro")
        render_relatorio_financeiro_retirada()
