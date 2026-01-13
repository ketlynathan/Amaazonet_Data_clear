import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from datetime import date, timedelta



# 🔥 Garante que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st

from app.ui.home import render_home
from app.ui.relatorios_app import render_relatorios
from app.ui.fechamento_tecnicos_app import render
from app.ui.ordens_servico_app import render_ordens_servico
from app.ui.fechamento_tecnicos_metabase_app import render_fechamento_metabase
from app.ui.usuarios_app import render_usuarios
from app.ui.relatorios_app import render_relatorios
from app.ui.ordens_servico_app import render_ordens_servico
from app.ui.relatorio_planilha_app import render_planilha
from app.ui.relatorio_financeiro_instalacoes_app import (
    render_relatorio_financeiro_instalacoes,
)
from app.ui.debug_financeiro_app import render_debug_sheets





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
        "Ordens de Serviço",
        "Relatórios",
        "Planilha Google",
        "Fechamento de Técnicos",  # 👈 NOVA OPÇÃO
        "Fechamento de Técnicos Metabase",
        "Relatório Financeiro Instalações",  # 👈 NOVA OPÇÃO
        "Debug Financeiro",
        

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

elif pagina == "Ordens de Serviço":
    render_ordens_servico()

elif pagina == "Fechamento de Técnicos":
    render()

elif pagina == "Fechamento de Técnicos Metabase":
    render_fechamento_metabase()

elif pagina == "Planilha Google":
    render_planilha()

elif pagina == "Relatório Financeiro Instalações":
    render_relatorio_financeiro_instalacoes()
    
elif pagina == "Debug Financeiro":
    render_debug_sheets()