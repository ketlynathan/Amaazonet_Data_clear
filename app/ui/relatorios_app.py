import streamlit as st
from app.ui.fechamento_tecnicos_metabase_app import render_fechamento_metabase
from app.ui.components.navigation import botao_voltar_home


def render_relatorios():
    botao_voltar_home()

    st.markdown("## 📊 Relatórios")

    tipo = st.tabs(["📅 Fechamento Mensal", "📆 Fechamento Semanal"])

    # ===============================
    # FECHAMENTO MENSAL
    # ===============================
    with tipo[0]:
        st.info("🛠 Módulo em desenvolvimento")
        st.write("O fechamento mensal será disponibilizado em breve.")

    # ===============================
    # FECHAMENTO SEMANAL
    # ===============================
    with tipo[1]:

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Fechamento Técnico", use_container_width=True):
                st.session_state["relatorio_subtela"] = "tecnico"

        with col2:
            st.button("📦 Fechamento Retirada", disabled=True, use_container_width=True)
            st.caption("Em manutenção")

        with col3:
            st.button("💰 Venda Autônomo", disabled=True, use_container_width=True)
            st.caption("Em manutenção")

        st.divider()

        # ===============================
        # RENDERIZA SUBTELAS
        # ===============================
        if st.session_state.get("relatorio_subtela") == "tecnico":
            render_fechamento_metabase()
