import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.relatorios.fechamento_tecnicos import (
    relatorio_fechamento_tecnicos_df
)

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="Relatório de Fechamento Técnico",
    layout="wide",
)

# ======================================================
# CACHE
# ======================================================
@st.cache_data(show_spinner=False)
def carregar_df(contas, data_inicio, data_fim, estados):
    return relatorio_fechamento_tecnicos_df(
        contas=contas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        estados=estados,
    )

# ======================================================
# APP
# ======================================================
def render():
    st.title("📋 Relatório de Fechamento Técnico")

    # =========================
    # SESSION STATE
    # =========================
    if "gerar_relatorio" not in st.session_state:
        st.session_state["gerar_relatorio"] = False

    if "df_base" not in st.session_state:
        st.session_state["df_base"] = pd.DataFrame()

    if "selecionados" not in st.session_state:
        st.session_state["selecionados"] = set()

    # =========================
    # RESET CONTROLADO
    # =========================
    def reset_relatorio():
        st.session_state["gerar_relatorio"] = False
        st.session_state["df_base"] = pd.DataFrame()
        st.session_state["selecionados"] = set()

    # =========================
    # SIDEBAR – FILTROS BASE
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania"],
            on_change=reset_relatorio,
        )

        hoje = date.today()

        data_inicio = st.date_input(
            "Data início",
            value=hoje - timedelta(days=7),
            on_change=reset_relatorio,
        )

        data_fim = st.date_input(
            "Data fim",
            value=hoje,
            on_change=reset_relatorio,
        )

        estados = st.multiselect(
            "Estado",
            ["AM", "PA"],
            default=["AM", "PA"],
            on_change=reset_relatorio,
        )

        if st.button("📊 Gerar relatório"):
            st.session_state["gerar_relatorio"] = True

    # =========================
    # CARGA BASE (UMA VEZ)
    # =========================
    if st.session_state["gerar_relatorio"] and st.session_state["df_base"].empty:
        with st.spinner("Carregando dados..."):
            df_base = carregar_df(
                contas, data_inicio, data_fim, estados
            )

        if df_base.empty:
            st.warning("Nenhuma ordem encontrada.")
            return

        st.session_state["df_base"] = df_base.copy()

    if not st.session_state["gerar_relatorio"]:
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

    # =========================
    # FILTROS DINÂMICOS
    # =========================
    st.subheader("🎯 Filtros dinâmicos")

    col1, col2 = st.columns(2)

    with col1:
        tipos_os = sorted(
            df_base["tipo_ordem_servico.descricao"]
            .dropna()
            .astype(str)
            .unique()
        )

        filtro_tipo = st.multiselect(
            "Tipo de Ordem de Serviço",
            tipos_os,
            default=tipos_os,
        )

    with col2:
        st.markdown("### 👷 Técnico")

        busca_tecnico = st.text_input(
        "Buscar técnico (ex: João, Silva, TEC)",
        placeholder="Digite parte do nome",
        )

        tecnicos_base = (
            df_base["usuario_fechamento.name"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    tecnicos_base = sorted(tecnicos_base)

    if busca_tecnico:
        tecnicos_filtrados = [
            t for t in tecnicos_base
            if busca_tecnico.lower() in t.lower()
        ]
    else:
        tecnicos_filtrados = tecnicos_base

    filtro_tecnico = st.multiselect(
        "Selecionar técnicos",
        tecnicos_filtrados,
        default=tecnicos_filtrados,
    )

    # =========================
    # APLICA FILTROS
    # =========================
    df = df_base.copy()

    if filtro_tipo:
        df = df[df["tipo_ordem_servico.descricao"].isin(filtro_tipo)]

    if filtro_tecnico:
        df = df[df["usuario_fechamento.name"].isin(filtro_tecnico)]

    if df.empty:
        st.warning("Nenhum registro após aplicar filtros.")
        return

    # =========================
    # ID ESTÁVEL
    # =========================
    df["_row_id"] = (
        df["numero"].astype(str)
        + "_"
        + df["dados_cliente.codigo_cliente"].astype(str)
    )

    # =========================
    # TABELA
    # =========================
    st.subheader("📑 Ordens de Serviço")

    colunas = [
        "_row_id",
        "numero",
        "tipo_ordem_servico.descricao",
        "usuario_fechamento.name",
        "dados_cliente.codigo_cliente",
        "dados_cliente.nome_razaosocial",
        "dados_endereco_instalacao.cidade",
        "dados_endereco_instalacao.estado",
    ]

    df_tela = df[colunas].copy()

    df_tela["Selecionar"] = df_tela["_row_id"].isin(
        st.session_state["selecionados"]
    )

    df_editado = st.data_editor(
        df_tela.drop(columns="_row_id"),
        hide_index=True,
        use_container_width=True,
        key="editor_os",
    )

    # =========================
    # SINCRONIZA SELEÇÃO
    # =========================
    for idx, row in df_tela.iterrows():
        row_id = row["_row_id"]
        marcado = df_editado.loc[idx, "Selecionar"]

        if marcado:
            st.session_state["selecionados"].add(row_id)
        else:
            st.session_state["selecionados"].discard(row_id)

    selecionados = df[
        df["_row_id"].isin(st.session_state["selecionados"])
    ]

    st.success(
        f"✅ {len(df)} registros | 🟢 {len(selecionados)} selecionados"
    )

    # =========================
    # COPIAR DADOS
    # =========================
    if not selecionados.empty:
        st.subheader("📋 Copiar dados selecionados")

        copiar_df = selecionados[
            [
                "numero",
                "dados_cliente.codigo_cliente",
                "dados_cliente.nome_razaosocial",
                "tipo_ordem_servico.descricao",
                "usuario_fechamento.name",
            ]
        ]

        st.text_area(
            "Copiar (Ctrl+C)",
            copiar_df.to_csv(index=False, sep="\t"),
            height=220,
        )
