import streamlit as st
from app.ui.components.navigation import botao_voltar_home

from app.ui.fechamento_tecnicos_app import render as render
from app.ui.fechamento_tecnicos_metabase_app import render_fechamento_metabase

def render_relatorios():
    # Botão de voltar Home
    botao_voltar_home()

    st.markdown("## 📊 Relatórios")
    st.markdown(
        "<p style='color:#666;font-size:14px;'>Selecione o tipo de fechamento desejado abaixo</p>",
        unsafe_allow_html=True
    )

    # Tabs Semanal x Mensal
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
        subtela = st.session_state.get("relatorio_subtela")
        
        # Aqui é o clique no card "Fechamento Técnico"
        if subtela == "tecnico":
            st.markdown("### Escolha o tipo de Fechamento Técnico:")
            tecnico_cols = st.columns(2, gap="medium")
            
            with tecnico_cols[0]:
                if st.button("📋 Fechamento Técnico (Hubsoft)", use_container_width=True):
                    st.session_state["tecnico_tipo"] = "local"
            
            with tecnico_cols[1]:
                if st.button("📋 Fechamento Técnico (Metabase)", use_container_width=True):
                    st.session_state["tecnico_tipo"] = "metabase"
            
            # Renderiza o relatório escolhido
            tecnico_tipo = st.session_state.get("tecnico_tipo")
            if tecnico_tipo == "local":
                with st.spinner("Carregando Fechamento Técnico Local..."):
                    render()
            elif tecnico_tipo == "metabase":
                with st.spinner("Carregando Fechamento Técnico Metabase..."):
                    render_fechamento_metabase()
