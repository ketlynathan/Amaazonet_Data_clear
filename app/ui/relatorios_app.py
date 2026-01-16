import streamlit as st
from app.ui.fechamento_tecnicos_metabase_app import render_fechamento_metabase
from app.ui.components.navigation import botao_voltar_home

def render_relatorios():
    # Botão de voltar Home
    botao_voltar_home()

    st.markdown("## 📊 Relatórios")
    st.markdown(
        "<p style='color:#666;font-size:14px;'>Selecione o tipo de fechamento desejado abaixo</p>",
        unsafe_allow_html=True
    )

    # Tabs para Semanal x Mensal
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

        # Layout em cards clicáveis
        cols = st.columns(3, gap="large")
        card_info = [
            {"label": "📋 Fechamento Técnico", "page": "tecnico", "enabled": True},
            {"label": "📦 Fechamento Retirada", "page": "retirada", "enabled": False},
            {"label": "💰 Venda Autônomo", "page": "venda", "enabled": False},
        ]

        for i, item in enumerate(card_info):
            with cols[i]:
                if item["enabled"]:
                    if st.button(item["label"], use_container_width=True):
                        st.session_state["relatorio_subtela"] = item["page"]
                else:
                    st.button(item["label"] + " (Em breve)", disabled=True, use_container_width=True)
                    st.caption("Em desenvolvimento")

        st.divider()

        # ===============================
        # RENDERIZA SUBTELAS
        # ===============================
        if st.session_state.get("relatorio_subtela") == "tecnico":
            with st.spinner("Carregando Fechamento Técnico..."):
                render_fechamento_metabase()
