import sys
from pathlib import Path
import streamlit as st

# ======================================================
# PYTHONPATH
# ======================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ======================================================
# IMPORTS UI
# ======================================================
from app.ui.home import render_home
from app.ui.usuarios_app import render_usuarios
from app.ui.ordens_servico_app import render_ordens_servico
from app.ui.relatorios_app import render_relatorios
from app.ui.relatorio_planilha_app import render_planilha
from app.ui.fechamento_tecnicos_app import render
from app.ui.fechamento_tecnicos_metabase_app import (
    render_fechamento_metabase,
)

# ======================================================
# PAGE CONFIG (sempre no topo)
# ======================================================
st.set_page_config(
    page_title="HubSoft Analytics",
    layout="wide",
)

# ======================================================
# NAVEGAÇÃO CENTRALIZADA
# ======================================================
PAGES = {
    "🏠 Home": render_home,
    "👤 Usuários": render_usuarios,
    "🛠️ Ordens de Serviço": render_ordens_servico,
    "📊 Relatórios": render_relatorios,
    "📄 Planilha Google": render_planilha,
    "📋 Fechamento de Técnicos": render,
    "📈 Fechamento Técnicos (Metabase)": render_fechamento_metabase,
}

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.title("📊 HubSoft Analytics")

pagina = st.sidebar.radio(
    "Navegação",
    list(PAGES.keys()),
)

# ======================================================
# RENDER
# ======================================================
PAGES[pagina]()
