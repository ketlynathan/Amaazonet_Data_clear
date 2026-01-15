import streamlit as st
from pathlib import Path

from app.ui.usuarios_app import render_usuarios
from app.ui.ordens_servico_app import render_ordens_servico
from app.ui.relatorios_app import render_relatorios


def render_home():

    # ===============================
    # LOGOS
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
            <div>
                <h1 style="margin-bottom:0;">HubSoft Analytics</h1>
                <p style="font-size:16px;color:#666;">
                    Plataforma corporativa de gestão, auditoria e relatórios
                </p>
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
            padding:15px;
            border-radius:8px;
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
    # CARDS DE STATUS
    # ===============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔌 Status", "Conectado")
    col2.metric("☁️ API", "HubSoft")
    col3.metric("🗄️ Base", "Produção")
    col4.metric("🕒 Última Sync", "Agora")

    st.write("")

    # ===============================
    # MENU DE ACESSO RÁPIDO
    # ===============================
    st.markdown("### 🚀 Acesso Rápido")

    a, b, c = st.columns(3)

    with a:
        if st.button("👤 Usuários", use_container_width=True):
            st.session_state.pagina = "Usuários"

    with b:
        if st.button("🛠️ Ordens de Serviço", use_container_width=True):
            st.session_state.pagina = "Ordens de Serviço"

    with c:
        if st.button("📈 Relatórios", use_container_width=True):
            st.session_state.pagina = "Relatórios"



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
