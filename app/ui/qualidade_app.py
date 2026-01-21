import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.ordens_servico import carregar_ordens_servico_df
from app.ui.components.navigation import botao_voltar_home

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
def render_qualidade():
    botao_voltar_home()
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

    