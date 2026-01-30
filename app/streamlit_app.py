import sys
from pathlib import Path
import streamlit as st

# 🔥 Adiciona raiz do projeto ao PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# ======================================================
# IMPORTAÇÃO DOS MÓDULOS DE UI
# ======================================================
from app.ui.home import render_home
from app.ui.relatorios_app import render_relatorios
from app.ui.ordens_servico_app import render_ordens_servico
from app.ui.usuarios_app import render_usuarios
from app.ui.relatorio_planilha_app import render_planilha
from app.ui.debug_financeiro_app import render_debug_sheets
from app.ui.naoUsado.fechamento_tecnicos_app import render
from app.ui.qualidade_app import render_qualidade
from app.ui.BackOffice_app import render_60_vendas

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="HubSoft Analytics",
    layout="wide",
)


# Inicializa estado
if "pagina" not in st.session_state:
    st.session_state.pagina = "Home"

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:

    # Wrapper do conteúdo
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)

    st.title("📊 HubSoft Analytics")
    st.markdown("### Navegação")
    st.caption("Selecione a página")

    opcoes = [
        "Home",
        "Usuários",
        "Ordens de Serviço",
        "Relatórios",
        "Planilha Google",
        "Debug Financeiro",
        "Qualidade",
        "Back Office",
    ]

    pagina = st.radio(
        "",
        opcoes,
        index=opcoes.index(st.session_state.pagina),
        label_visibility="collapsed",
    )
    st.session_state.pagina = pagina

    if st.session_state.pagina != "Home":
        if st.button("⬅ Voltar para Home", key="btn_voltar_home_sidebar"):
            st.session_state.pagina = "Home"
            st.experimental_rerun()

    



# ======================================================
# ROTEAMENTO DAS PÁGINAS
# ======================================================
if pagina == "Home":
    render_home()
elif pagina == "Usuários":
    render_usuarios()
elif pagina == "Ordens de Serviço":
    render_ordens_servico()
elif pagina == "Relatórios":
    render_relatorios()
elif pagina == "Fechamento de Técnicos":
    render()
elif pagina == "Planilha Google":
    render_planilha()
elif pagina == "Debug Financeiro":
    render_debug_sheets()
elif pagina == "Qualidade":
    render_qualidade()
elif pagina == "Back Office":
    render_60_vendas()
else:
    st.warning("Página em construção 🚧")
