import streamlit as st
from pathlib import Path


# ======================================================
# RESOLUÇÃO ROBUSTA DE CAMINHO (LOCAL + DOCKER)
# ======================================================
# home.py -> /app/app/ui/home.py
BASE_DIR = Path(__file__).resolve().parents[1]  # /app/app
IMG_DIR = BASE_DIR / "img"


def render_home():

    # ======================================================
    # HEADER
    # ======================================================
    col_logo1, col_title, col_logo2 = st.columns([2, 4, 2])

    with col_logo1:
        amazonet_img = IMG_DIR / "amazonet.png"
        if amazonet_img.exists():
            st.image(str(amazonet_img), width=130)

    with col_title:
        cols = st.columns([0.4, 7.6])

        with cols[0]:
            st.write("")
            st.write("")
            hub_img = IMG_DIR / "hub.png"
            if hub_img.exists():
                st.image(str(hub_img), width=50)
            else:
                st.warning("Imagem hub.png não encontrada")

        with cols[1]:
            st.markdown(
                """
                <div style="text-align:left;">
                    <h1 style="margin-bottom:4px;">HubSoft Analytics</h1>
                    <p style="font-size:15px;opacity:0.7;">
                        Plataforma corporativa de gestão, auditoria e relatórios
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_logo2:
        mania_img = IMG_DIR / "mania.png"
        if mania_img.exists():
            st.image(str(mania_img), width=130)

    st.divider()

    # ======================================================
    # FRASE INSTITUCIONAL (CENTRALIZADA DE VERDADE)
    # ======================================================
    col_left, col_center, col_right = st.columns([2, 6, 2])

    with col_center:
        st.info(
            "Central de dados, indicadores e automações operacionais do Grupo AMZ",
            icon="📊",
        )

    # ======================================================
    # STATUS GERAL (SAFE PARA DARK MODE)
    # ======================================================
    st.subheader("🔌 Status do Sistema")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Status", "Conectado")
    c2.metric("API", "HubSoft")
    c3.metric("Base", "Produção")
    c4.metric("Última Sync", "Agora")

    # ======================================================
    # ACESSO RÁPIDO
    # ======================================================
    st.subheader("🚀 Acesso Rápido")

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

    st.divider()

    # ======================================================
    # RODAPÉ
    # ======================================================
    st.markdown(
        "<div style='text-align:center; font-size:12px; opacity:0.6;'>"
        "HubSoft Analytics © 2026 — Amazonet & Mania Telecom<br>"
        "Desenvolvimento: Ketlyn Athan"
        "</div>",
        unsafe_allow_html=True,
    )
