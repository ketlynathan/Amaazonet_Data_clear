import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.relatorios.fechamento_tecnicos import (
<<<<<<< HEAD
    relatorio_fechamento_tecnicos_df,
)

# ======================================================
# CONSTANTES
# ======================================================
COL_TECNICO = "usuario_fechamento.name"
COL_TIPO_OS = "tipo_ordem_servico.descricao"

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
=======
    relatorio_fechamento_tecnicos_df
)

# ======================================================
>>>>>>> origin/dev
# CONFIG
# ======================================================
st.set_page_config(
    page_title="Relatório de Fechamento Técnico",
    layout="wide",
)

# ======================================================
<<<<<<< HEAD
# CACHE – CARGA ÚNICA DA API
# ======================================================
@st.cache_data(ttl=900)
def carregar_df_base(contas, data_inicio, data_fim, estados):
=======
# CACHE
# ======================================================
@st.cache_data(show_spinner=False)
def carregar_df(contas, data_inicio, data_fim, estados):
>>>>>>> origin/dev
    return relatorio_fechamento_tecnicos_df(
        contas=contas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        estados=estados,
    )

# ======================================================
<<<<<<< HEAD
# FUNÇÕES AUXILIARES
# ======================================================
def obter_tipos_validos_por_conta(df: pd.DataFrame) -> list[str]:
    """
    Retorna apenas os tipos de OS válidos
    de acordo com as contas presentes no dataframe.
    """
    tipos = set()

    if "conta" not in df.columns:
        return []

    for conta in df["conta"].dropna().str.lower().unique():
        tipos.update(
            TIPOS_OS_FECHAMENTO_POR_CONTA.get(conta, [])
        )

    return sorted(tipos)

# ======================================================
=======
>>>>>>> origin/dev
# APP
# ======================================================
def render():
    st.title("📋 Relatório de Fechamento Técnico")

    # =========================
    # SESSION STATE
    # =========================
<<<<<<< HEAD
    st.session_state.setdefault("df_base", pd.DataFrame())
    st.session_state.setdefault("carregado", False)
=======
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
>>>>>>> origin/dev

    # =========================
    # SIDEBAR – FILTROS BASE
    # =========================
    with st.sidebar:
<<<<<<< HEAD
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas",
            ["amazonet", "mania"],
            default=["amazonet"],
=======
        st.subheader("🔎 Filtros")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania"],
            on_change=reset_relatorio,
>>>>>>> origin/dev
        )

        hoje = date.today()

        data_inicio = st.date_input(
            "Data início",
            value=hoje - timedelta(days=7),
<<<<<<< HEAD
=======
            on_change=reset_relatorio,
>>>>>>> origin/dev
        )

        data_fim = st.date_input(
            "Data fim",
            value=hoje,
<<<<<<< HEAD
        )

        estados = st.multiselect(
            "Estados",
            ["AM", "PA"],
            default=["AM", "PA"],
        )

        gerar = st.button("📊 Gerar relatório")

    # =========================
    # CARGA DA API (UMA VEZ)
    # =========================
    if gerar:
        if not contas:
            st.error("Selecione ao menos uma conta")
            return

        if data_inicio > data_fim:
            st.error("Data início maior que data fim")
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
=======
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
>>>>>>> origin/dev
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

<<<<<<< HEAD
    # ======================================================
    # FILTROS PÓS-CARGA (SEM API)
    # ======================================================
    st.subheader("🎯 Filtros")

    col1, col2 = st.columns(2)

    # ----------- TÉCNICO -----------
    with col1:
        st.markdown("### 👷 Técnico")

        busca_tecnico = st.text_input(
            "Buscar técnico",
            placeholder="Ex: Edinelson, Moura, TEC",
        )

        tecnicos = (
            df_base[COL_TECNICO]
=======
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
>>>>>>> origin/dev
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
<<<<<<< HEAD
        tecnicos = sorted(tecnicos)

        if busca_tecnico:
            tecnicos = [
                t for t in tecnicos
                if busca_tecnico.lower() in t.lower()
            ]

        filtro_tecnico = st.multiselect(
            "Selecionar técnico(s)",
            tecnicos,
            default=tecnicos,
        )

    # ----------- TIPO DE OS (POR CONTA) -----------
    with col2:
        st.markdown("### 🧾 Tipo de Ordem de Serviço")

        tipos_validos = obter_tipos_validos_por_conta(df_base)

        filtro_tipo_os = st.multiselect(
            "Tipos válidos para fechamento",
            tipos_validos,
            default=tipos_validos,
        )
=======

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
>>>>>>> origin/dev

    # =========================
    # APLICA FILTROS
    # =========================
    df = df_base.copy()

<<<<<<< HEAD
    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_tipo_os:
        df = df[df[COL_TIPO_OS].isin(filtro_tipo_os)]

    if df.empty:
        st.warning("Nenhum registro após aplicar os filtros.")
        return

    # =========================
    # RESULTADO
    # =========================
    st.success(f"✅ {len(df)} ordens válidas para fechamento")

    colunas_exibir = [
        "numero",
        COL_TIPO_OS,
        COL_TECNICO,
=======
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
>>>>>>> origin/dev
        "dados_cliente.codigo_cliente",
        "dados_cliente.nome_razaosocial",
        "dados_endereco_instalacao.cidade",
        "dados_endereco_instalacao.estado",
<<<<<<< HEAD
        "conta",
        "status",
        "data_termino_executado",
    ]

    colunas_exibir = [c for c in colunas_exibir if c in df.columns]

    st.dataframe(
        df[colunas_exibir],
        use_container_width=True,
        hide_index=True,
    )

    # =========================
    # EXPORTAÇÃO
    # =========================
    st.download_button(
        "⬇️ Exportar CSV",
        df[colunas_exibir].to_csv(index=False),
        file_name="relatorio_fechamento_tecnico.csv",
        mime="text/csv",
    )
=======
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
>>>>>>> origin/dev
