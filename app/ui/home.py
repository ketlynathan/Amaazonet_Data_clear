import streamlit as st
from pathlib import Path

def render_home():

    # ===============================
    # HEADER COM LOGOS
    # ===============================
    col_logo1, col_title, col_logo2 = st.columns([1, 3, 1])

    with col_logo1:
        if Path("app/img/amazonet.png").exists():
            st.image("app/img/amazonet.png", width=120)

    with col_title:
        cols = st.columns([1, 6])
        if Path("app/img/hub.png").exists():
            cols[0].image("app/img/hub.png", width=60)

        cols[1].markdown(
            """
            <div style="text-align:center;">
                <h1 style="margin-bottom:5px;color:#4B8BBE;">HubSoft Analytics</h1>
                <p style="font-size:16px;color:#666;">Plataforma corporativa de gestão, auditoria e relatórios</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_logo2:
        if Path("app/img/mania.png").exists():
            st.image("app/img/mania.png", width=120)

    st.markdown("---")

    # ===============================
    # FRASE INSTITUCIONAL
    # ===============================
    st.markdown(
        """
        <div style="
            background:#f2f2f2;
            padding:20px;
            border-radius:10px;
            text-align:center;
            font-size:16px;
            font-weight:600;
        ">
            Central de dados, indicadores e automações operacionais do Grupo AMZ
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # ===============================
    # CARDS DE STATUS CUSTOMIZADOS
    # ===============================
    status_cards = [
        {"title": "🔌 Status", "value": "Conectado", "color": "#DFF6DD"},
        {"title": "☁️ API", "value": "HubSoft", "color": "#E0F0FF"},
        {"title": "🗄️ Base", "value": "Produção", "color": "#FFF4E0"},
        {"title": "🕒 Última Sync", "value": "Agora", "color": "#FFE0E0"},
    ]

    cols = st.columns(4)
    for i, card in enumerate(status_cards):
        cols[i].markdown(
            f"""
            <div style="
                background:{card['color']};
                border-radius:10px;
                padding:20px;
                text-align:center;
                font-weight:bold;
                font-size:18px;
            ">
                <div>{card['title']}</div>
                <div style="font-size:24px;margin-top:5px;">{card['value']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # ===============================
    # MENU DE ACESSO RÁPIDO COMO CARDS
    # ===============================
    st.markdown("### 🚀 Acesso Rápido")
    menu_items = [
        {"label": "👤 Usuários", "page": "Usuários", "color": "#4B8BBE"},
        {"label": "🛠️ Ordens de Serviço", "page": "Ordens de Serviço", "color": "#FF8C42"},
        {"label": "📈 Relatórios", "page": "Relatórios", "color": "#42B883"},
    ]

    cols = st.columns(3)
    for i, item in enumerate(menu_items):
        if cols[i].button(item["label"], use_container_width=True):
            st.session_state.pagina = item["page"]

    st.markdown("---")

    # ===============================
    # RODAPÉ
    # ===============================
    st.markdown(
        """
        <div style="text-align:center;color:#999;font-size:12px;">
            HubSoft Analytics © 2026 — Amazonet & Mania Telecom
        </div>
        """,
        unsafe_allow_html=True
    )
