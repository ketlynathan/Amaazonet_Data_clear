import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.relatorios.fechamento_tecnicos import (
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
# CONFIG
# ======================================================
st.set_page_config(
    page_title="Relatório de Fechamento Técnico",
    layout="wide",
)

# ======================================================
# CACHE – CARGA ÚNICA DA API
# ======================================================
@st.cache_data(ttl=900)
def carregar_df_base(contas, data_inicio, data_fim, estados):
    return relatorio_fechamento_tecnicos_df(
        contas=contas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        estados=estados,
    )

# ======================================================
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
# APP
# ======================================================
def render():
    st.title("📋 Relatório de Fechamento Técnico")

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
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df_base = st.session_state["df_base"]

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
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
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

    # =========================
    # RESULTADO
    # =========================
    st.success(f"✅ {len(df)} ordens válidas para fechamento")

    colunas_exibir = [
        "numero",
        COL_TIPO_OS,
        COL_TECNICO,
        "dados_cliente.codigo_cliente",
        "dados_cliente.nome_razaosocial",
        "dados_endereco_instalacao.cidade",
        "dados_endereco_instalacao.estado",
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
