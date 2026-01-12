import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.ordens_servico import carregar_ordens_servico_df

# ======================================================
# CONSTANTES DE COLUNAS (API REAL)
# ======================================================
COL_STATUS = "status"
COL_TECNICO = "usuario_fechamento.name"
COL_ESTADO = "dados_endereco_instalacao.estado"

STATUS_MONITORADOS = [
    "Finalizado",
    "Pendente",
]

# ======================================================
# APP
# ======================================================
def render_ordens_servico():
    st.title("🛠 Ordens de Serviço – HubSoft")

    # ======================================================
    # SESSION STATE (ANTI-QUEBRA)
    # ======================================================
    st.session_state.setdefault("df_os", pd.DataFrame())
    st.session_state.setdefault("carregado", False)

    # ======================================================
    # SIDEBAR – FILTROS BASE
    # ======================================================
    with st.sidebar:
        st.subheader("🔎 Filtros base")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania", "amazonet"],
        )

        hoje = date.today()

        data_inicio = st.date_input(
            "Data início",
            hoje - timedelta(days=7),
        )

        data_fim = st.date_input(
            "Data fim",
            hoje,
        )

        carregar = st.button("📥 Carregar ordens")

    # ======================================================
    # CARREGAMENTO
    # ======================================================
    if carregar:
        if not contas:
            st.warning("Selecione ao menos uma conta.")
            return

        with st.spinner("🔄 Carregando ordens de serviço..."):
            dfs = []

            for conta in contas:
                df_conta = carregar_ordens_servico_df(
                    conta=conta,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )

                if not df_conta.empty:
                    dfs.append(df_conta)

        if not dfs:
            st.warning("Nenhuma ordem encontrada.")
            st.session_state["carregado"] = False
            return

        df = pd.concat(dfs, ignore_index=True)

        # garante colunas críticas
        for col in [COL_STATUS, COL_TECNICO, COL_ESTADO]:
            if col not in df.columns:
                df[col] = None

        st.session_state["df_os"] = df
        st.session_state["carregado"] = True

    # ======================================================
    # AGUARDA CARGA
    # ======================================================
    if not st.session_state["carregado"]:
        st.info("Selecione os filtros e clique em **📥 Carregar ordens**")
        return

    df_base = st.session_state["df_os"]

    # ======================================================
    # KPIs / CARDS
    # ======================================================
    st.subheader("📊 Resumo")

    total_os = len(df_base)

    cols = st.columns(len(STATUS_MONITORADOS) + 1)

    cols[0].metric("Total OS", total_os)

    for i, status in enumerate(STATUS_MONITORADOS, start=1):
        total_status = len(df_base[df_base[COL_STATUS] == status])
        cols[i].metric(status, total_status)

    # ======================================================
    # FILTROS PÓS-CARGA
    # ======================================================
    st.subheader("🎯 Filtros")

    col1, col2 = st.columns(2)

    # -------- TÉCNICO --------
    with col1:
        busca_tecnico = st.text_input(
            "🔍 Buscar técnico",
            placeholder="Digite parte do nome",
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

    # -------- ESTADO --------
    with col2:
        estados = (
            df_base[COL_ESTADO]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        estados.sort()

        filtro_estado = st.multiselect(
            "📍 Estado",
            estados,
            default=estados,
        )

    # ======================================================
    # APLICA FILTROS
    # ======================================================
    df = df_base.copy()

    if filtro_tecnico:
        df = df[df[COL_TECNICO].isin(filtro_tecnico)]

    if filtro_estado:
        df = df[df[COL_ESTADO].isin(filtro_estado)]

    if df.empty:
        st.warning("Nenhuma ordem encontrada com os filtros aplicados.")
        return

    st.success(f"✅ {len(df)} ordens encontradas")

    # ======================================================
    # TABELA COMPLETA (TUDO DA API)
    # ======================================================
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )

    # ======================================================
    # EXPORTAÇÃO
    # ======================================================
    st.download_button(
        "⬇️ Exportar CSV",
        df.to_csv(index=False),
        file_name="ordens_servico_hubsoft.csv",
        mime="text/csv",
    )
