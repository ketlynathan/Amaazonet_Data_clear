import sys
from pathlib import Path

# 🔥 Garante que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.ui.home import render_home
from app.ui.relatorios_app import render_relatorios
from app.ui.usuarios_app import render_usuarios


st.set_page_config(
    page_title="HubSoft Analytics",
    layout="wide",
)

st.sidebar.title("📊 HubSoft Analytics")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Home",
        "Usuários",
        "Relatórios",
    ],
)

# ======================================================
# ROTEAMENTO CORRETO
# ======================================================
if pagina == "Home":
    render_home()

elif pagina == "Usuários":
    render_usuarios()

elif pagina == "Relatórios":
    render_relatorios()
