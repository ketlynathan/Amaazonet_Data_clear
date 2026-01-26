import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.metabase_service import carregar_fila_metabase

COL_VENDEDOR = "usuario_abertura"


TIPOS_OS_FECHAMENTO_POR_CONTA = {
    "amazonet": [
        "INSTALAÇÃO (R$ 100,00)",
        "INSTALAÇÃO (R$ 49,90)",
        "INSTALAÇÃO GRÁTIS",
    ],
    "mania": [
        "INSTALAÇÃO (R$ 20,00)",
        "INSTALAÇÃO WI-FI+ (R$ 20,00)",
        "INSTALAÇÃO (R$ 100,00)",
    ],
}


@st.cache_data(ttl=900, show_spinner=False)
def carregar_base_bruta(contas, data_inicio, data_fim):
    dfs = []
    for conta in contas:
        df = carregar_fila_metabase(conta, data_inicio, data_fim)
        if not df.empty:
            df["_conta_origem_debug"] = conta.lower()
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


def render_venda_metabase():
    st.title("📦 Relatório de Vendas")

    # =========================
    # SESSION STATE
    # =========================
    st.session_state.setdefault("df_vendas_base", pd.DataFrame())
    st.session_state.setdefault("dados_carregados_vendas", False)

    # =========================
    # SIDEBAR (FILTROS DE CARGA)
    # =========================
    with st.sidebar:
        st.subheader("🎛️ Filtros de Carga")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania"],
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início (cadastro OS)", hoje - timedelta(days=30))
        data_fim = st.date_input("Data fim (cadastro OS)", hoje)

        gerar = st.button("🚀 Gerar Relatório")

    # =========================
    # CARGA (SÓ QUANDO CLICA)
    # =========================
    if gerar:
        with st.spinner("🔄 Carregando dados do Metabase..."):
            df = carregar_base_bruta(contas, data_inicio, data_fim)

        if df.empty:
            st.error("Metabase não retornou dados.")
            return

        df["data_cadastro_os"] = pd.to_datetime(df["data_cadastro_os"], errors="coerce")
        df["data_termino_executado"] = pd.to_datetime(df["data_termino_executado"], errors="coerce")

        df["cidade"] = df["cidade"].astype(str).str.strip().str.title()
        df["usuario_abertura"] = df["usuario_abertura"].astype(str).str.strip().str.upper()
        df["tipo_ordem_servico"] = df["tipo_ordem_servico"].astype(str).str.strip()

        df = df[
            (df["data_cadastro_os"].dt.date >= data_inicio) &
            (df["data_cadastro_os"].dt.date <= data_fim)
        ]

        df = df[
            df.apply(
                lambda row: row["tipo_ordem_servico"] in TIPOS_OS_FECHAMENTO_POR_CONTA.get(row["_conta_origem_debug"], []),
                axis=1
            )
        ]

        if df.empty:
            st.warning("Nenhuma venda encontrada.")
            return

        df_vendas = df[[
            "codigo_cliente",
            "data_cadastro_os",
            "data_termino_executado",
            "numero_ordem_servico",
            "nome_cliente",
            "vendedor",
            "usuario_abertura",
            "status",
            "cidade",
            "tipo_ordem_servico",
            "_conta_origem_debug",
        ]].copy()

        df_vendas.rename(columns={
            "data_cadastro_os": "data_abertura_os",
            "data_termino_executado": "data_conclusao_os",
            "_conta_origem_debug": "conta",
        }, inplace=True)

        df_vendas = df_vendas.loc[:, ~df_vendas.columns.duplicated()]
        df_vendas = df_vendas.sort_values("data_abertura_os", ascending=False)

        st.session_state["df_vendas_base"] = df_vendas
        st.session_state["dados_carregados_vendas"] = True

    import streamlit as st
import pandas as pd
from datetime import date, timedelta
from app.analysis.google_sheets import read_sheet_as_dataframe

def render_60_vendas():
    """
    Renderiza a aba de vendas da Planilha 60 com filtros laterais.
    """

    st.subheader("📄 Planilha 60 (Vendas) - ANÁLISE E CADASTRO")

    # =========================
    # Leitura da aba a partir da linha 11218
    # =========================
    with st.spinner("Lendo planilha 60 (vendas)..."):
        sheet_60_venda = read_sheet_as_dataframe("60_venda", start_row=11218)

    if sheet_60_venda.empty:
        st.error("Planilha 60 (vendas) vazia.")
        return

    # ------------------------------
    # Selecionar colunas de interesse
    # ------------------------------
    df60_venda_debug = sheet_60_venda.iloc[:, [0, 1, 4, 5, 6, 10]].copy()
    df60_venda_debug.columns = [
        "status_analise",
        "vendedor",
        "cod_cliente",
        "cod_os",
        "empresa",      # MANIA TELECOM / AMAZONET
        "tipo_venda",   # A VENDA É DE UM:
    ]

    # Limpar valores
    for c in df60_venda_debug.columns:
        df60_venda_debug[c] = df60_venda_debug[c].astype(str).str.strip()

    # ------------------------------
    # Adicionar colunas auxiliares
    # ------------------------------
    df60_venda_debug["back"] = sheet_60_venda.iloc[:, 3].astype(str).str.strip()  # coluna D original
    df60_venda_debug["data_fechamento"] = pd.to_datetime(sheet_60_venda.iloc[:, 7], errors="coerce")  # coluna 7 = Data termino

    # =========================
    # Sidebar de filtros
    # =========================
    with st.sidebar:
        st.subheader("🎛️ Filtros de Vendas")

        # Filtro por empresa
        empresas = sorted(df60_venda_debug["empresa"].dropna().unique())
        selected_empresas = st.multiselect(
            "Empresa",
            empresas,
            default=empresas
        )

        # Filtro por Back
        back_options = ["Todos"] + sorted(df60_venda_debug["back"].dropna().unique())
        selected_back = st.selectbox("Back", back_options)

        # Filtro período
        hoje = date.today()
        min_date = df60_venda_debug["data_fechamento"].min().date()
        max_date = df60_venda_debug["data_fechamento"].max().date()
        data_inicio = st.date_input("Data início (fechamento)", min_value=min_date, max_value=max_date, value=min_date)
        data_fim = st.date_input("Data fim (fechamento)", min_value=min_date, max_value=max_date, value=max_date)

    # =========================
    # Aplicar filtros
    # =========================
    df_filtrado = df60_venda_debug.copy()

    if selected_empresas:
        df_filtrado = df_filtrado[df_filtrado["empresa"].isin(selected_empresas)]

    if selected_back != "Todos":
        df_filtrado = df_filtrado[df_filtrado["back"] == selected_back]

    df_filtrado = df_filtrado[
        (df_filtrado["data_fechamento"].dt.date >= data_inicio) &
        (df_filtrado["data_fechamento"].dt.date <= data_fim)
    ]

    # =========================
    # Mostrar resultados
    # =========================
    st.success(f"✅ {len(df_filtrado)} vendas encontradas")
    st.dataframe(df_filtrado, use_container_width=True)

    # ------------------------------
    # Distribuição por vendedor
    # ------------------------------
    st.subheader("📊 Distribuição por Vendedor")
    st.dataframe(
        df_filtrado["vendedor"]
        .value_counts(dropna=False)
        .reset_index()
        .rename(columns={"index": "vendedor", "vendedor": "qtd"})
    )
