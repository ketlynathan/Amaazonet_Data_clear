import sys
from pathlib import Path

# 🔥 Garante que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.ui.home import render_home
from app.ui.usuarios_app import render_usuarios
from app.ui.relatorios_app import render_relatorios
from app.ui.fechamento_tecnicos_app import render_relatorio_fechamento_tecnico
from app.ui.ordens_servico_app import render_ordens_servico


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
        "Ordem de serviço",
        "Relatórios",
        "Fechamento de Técnicos",  # 👈 NOVA OPÇÃO
    ],
)

# ======================================================
# ROTEAMENTO
# ======================================================
if pagina == "Home":
    render_home()

elif pagina == "Usuários":
    render_usuarios()

elif pagina == "Ordem de serviço":
    render_ordens_servico()

elif pagina == "Relatórios":
    render_relatorios()

elif pagina == "Fechamento de Técnicos":
    render_relatorio_fechamento_tecnico()
