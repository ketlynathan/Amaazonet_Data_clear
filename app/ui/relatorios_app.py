import streamlit as st
from app.ui.components.navigation import botao_voltar_home

from app.ui.fechamento_tecnicos_app import render 
from app.ui.fechamento_tecnicos_metabase_app import render_fechamento_metabase

from app.ui.fechamento_retirada_metabase_app import render_retirada_metabase
from app.ui.fechamento_retirada_app import render_retirada

def render_relatorios():
    botao_voltar_home()

    st.markdown("## 📊 Relatórios")
    st.markdown(
        "<p style='color:#666;font-size:14px;'>Selecione o tipo de fechamento desejado abaixo</p>",
        unsafe_allow_html=True
    )

    tabs = st.tabs(["📆 Fechamento Semanal", "📅 Fechamento Mensal"])

    # ===============================
    # FECHAMENTO MENSAL
    # ===============================
    with tabs[1]:
        st.info("🛠 Módulo em desenvolvimento")
        st.write("O fechamento mensal será disponibilizado em breve.")

    # ===============================
    # FECHAMENTO SEMANAL
    # ===============================
    with tabs[0]:

        cols = st.columns(3, gap="large")

        card_info = [
            {"label": "📋 Fechamento Técnico", "page": "tecnico", "enabled": True},
            {"label": "📦 Fechamento Retirada", "page": "retirada", "enabled": True},
            {"label": "💰 Venda Autônomo", "page": "venda", "enabled": False},
        ]

        for i, item in enumerate(card_info):
            with cols[i]:
                if item["enabled"]:
                    if st.button(item["label"], use_container_width=True):
                        st.session_state["relatorio_subtela"] = item["page"]
                        st.session_state.pop("tecnico_tipo", None)
                        st.session_state.pop("retirada_tipo", None)
                else:
                    st.button(item["label"] + " (Em breve)", disabled=True, use_container_width=True)
                    st.caption("Em desenvolvimento")

        st.divider()

        subtela = st.session_state.get("relatorio_subtela")

        # ======================================================
        # FECHAMENTO TÉCNICO
        # ======================================================
        if subtela == "tecnico":
            st.markdown("### 📋 Fechamento Técnico")
            cols = st.columns(2, gap="medium")

            with cols[0]:
                if st.button("Hubsoft", use_container_width=True):
                    st.session_state["tecnico_tipo"] = "local"

            with cols[1]:
                if st.button("Metabase", use_container_width=True):
                    st.session_state["tecnico_tipo"] = "metabase"

            tecnico_tipo = st.session_state.get("tecnico_tipo")

            if tecnico_tipo == "local":
                with st.spinner("Carregando Fechamento Técnico (Hubsoft)..."):
                    render()

            elif tecnico_tipo == "metabase":
                with st.spinner("Carregando Fechamento Técnico (Metabase)..."):
                    render_fechamento_metabase()

        # ======================================================
        # FECHAMENTO RETIRADA
        # ======================================================
        elif subtela == "retirada":
            st.markdown("### 📦 Fechamento Retirada")
            cols = st.columns(2, gap="medium")

            with cols[0]:
                if st.button("Hubsoft", use_container_width=True):
                    st.session_state["retirada_tipo"] = "local"

            with cols[1]:
                if st.button("Metabase", use_container_width=True):
                    st.session_state["retirada_tipo"] = "metabase"

            retirada_tipo = st.session_state.get("retirada_tipo")

            if retirada_tipo == "local":
                with st.spinner("Carregando Fechamento Retirada (Hubsoft)..."):
                    render_retirada()

            elif retirada_tipo == "metabase":
                with st.spinner("Carregando Fechamento Retirada (Metabase)..."):
                    render_retirada_metabase()
