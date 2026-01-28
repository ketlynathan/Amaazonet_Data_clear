import streamlit as st
import pandas as pd
from datetime import date
from app.analysis.metabase_service import carregar_fila_metabase
from app.ui.relatorios_finaceiro_vendas_app import render_relatorio_financeiro_vendas


COL_VENDEDOR = "vendedor"
UNIDADES = {
    "STM": ["Santarém"],

    "REGIONAIS PA": [
        "Alenquer", "Marabá", "Prainha",
        "Monte Alegre", "Óbidos", "Oriximiná",
        "Belterra", "Mojuí Dos Campos", "Itaituba",
        "Curuá", "Uruará", "Alter Do Chão",
    ],

    "MAO": ["Manaus"],

    "REGIONAIS AM": [
        "Presidente Figueiredo",
        "Manacapuru",
        "Iranduba",
        "Parintins",
        "Itacoatiara",
        "Rio Preto Da Eva"
    ],
}



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
    # SIDEBAR — FILTROS DE CARGA
    # =========================
    with st.sidebar:
        st.subheader("🎛️ Filtros de Carga")

        contas = st.multiselect(
            "conta",
            ["mania", "amazonet"],
            default=["mania"],
        )

        hoje = date.today()
        data_inicio = st.date_input("Data início (cadastro OS)")
        data_fim = st.date_input("Data fim (cadastro OS)", hoje)

        gerar = st.button("🚀 Gerar Relatório")

    # =========================
    # CARGA DOS DADOS
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
        df["vendedor"] = df["vendedor"].astype(str).str.strip().str.title()

        df = df[
            (df["data_termino_executado"].dt.date >= data_inicio) &
            (df["data_termino_executado"].dt.date <= data_fim)
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

        df_vendas = df_vendas.sort_values("data_abertura_os", ascending=False)

        st.session_state["df_vendas_base"] = df_vendas
        st.session_state["dados_carregados_vendas"] = True

    # =========================
    # EXIBIÇÃO + FILTROS PÓS-CARGA
    # =========================
    if st.session_state["dados_carregados_vendas"]:

        df_base = st.session_state["df_vendas_base"]

        if df_base.empty:
            st.warning("Sem dados carregados.")
            return

        st.success(f"✅ {len(df_base)} vendas encontradas")

        # =========================
        # FILTROS
        # =========================
        st.subheader("🎯 Filtros")

        col1, col2, col3 = st.columns(3)

        # -------- VENDEDOR --------
        with col1:
            st.markdown("### Vendedor")

            busca_vendedor = st.text_input("Buscar vendedor")

            vendedores = (
                df_base["vendedor"]
                .dropna()
                .astype(str)
                .str.strip()
                .sort_values()
                .unique()
                .tolist()
            )

            if busca_vendedor:
                vendedores = [v for v in vendedores if busca_vendedor.lower() in v.lower()]

            filtro_vendedor = st.multiselect(
                "Selecionar vendedor(es)",
                vendedores,
                default=vendedores,
            )


        # -------- BACK OFFICE --------
        with col2:
            st.markdown("### Back Office")

            busca_bo = st.text_input("Buscar Back Office")

            backoffices = (
                df_base["usuario_abertura"]
                .dropna()
                .astype(str)
                .str.strip()
                .sort_values()
                .unique()
                .tolist()
            )

            if busca_bo:
                backoffices = [b for b in backoffices if busca_bo.lower() in b.lower()]

            filtro_backoffice = st.multiselect(
                "Selecionar Back Office(s)",
                backoffices,
                default=backoffices,
            )


        # -------- UNIDADE --------
        with col3:
            st.markdown("### Unidade")

            unidades_disponiveis = list(UNIDADES.keys())

            filtro_unidade = st.multiselect(
                "Selecionar unidade(s)",
                unidades_disponiveis,
                default=unidades_disponiveis,
            )
        
        df_filtrado = df_base.copy()

        # Filtro vendedor
        if filtro_vendedor:
            df_filtrado = df_filtrado[df_filtrado["vendedor"].isin(filtro_vendedor)]

        # Filtro back office
        if filtro_backoffice:
            df_filtrado = df_filtrado[df_filtrado["usuario_abertura"].isin(filtro_backoffice)]

        # Filtro unidade (cidade agrupada)
        if filtro_unidade:
            cidades_permitidas = []

            for unidade in filtro_unidade:
                cidades_permitidas.extend(UNIDADES.get(unidade, []))

            df_filtrado = df_filtrado[df_filtrado["cidade"].isin(cidades_permitidas)]
        
        st.markdown("## 📊 Resumo Geral")

        colA, colB, colC = st.columns(3)

        total_os = len(df_filtrado)
        total_vendedores = df_filtrado["vendedor"].nunique()
        total_unidades = df_filtrado["cidade"].map(
            lambda c: next((u for u, cidades in UNIDADES.items() if c in cidades), None)
        ).nunique()

        colA.metric("Total de Vendas", total_os)
        colB.metric("Vendedores Ativos", total_vendedores)
        colC.metric("Unidades Atendidas", total_unidades)

        def mapear_unidade(cidade):
            for unidade, cidades in UNIDADES.items():
                if cidade in cidades:
                    return unidade
            return "Outra"

        df_filtrado["unidade"] = df_filtrado["cidade"].apply(mapear_unidade)
        st.markdown("## 🏙️ Vendas por Unidade")

        vendas_unidade = (
            df_filtrado.groupby("unidade")
            .size()
            .reset_index(name="Total de Vendas")
            .sort_values("Total de Vendas", ascending=False)
        )

        st.dataframe(vendas_unidade, use_container_width=True)




        st.success(f"📊 {len(df_filtrado)} ordens após filtros")

        st.dataframe(df_filtrado, use_container_width=True)
        # 🔗 DISPONIBILIZA PARA O FINANCEIRO
        st.session_state["df_fechamento_filtrado"] = df_filtrado
        
        if not df_filtrado.empty:
            st.markdown("---")
            st.markdown("---")
            render_relatorio_financeiro_vendas()
