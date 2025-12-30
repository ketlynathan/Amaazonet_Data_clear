import streamlit as st
import pandas as pd

from app.analysis.usuarios import carregar_usuarios_df


@st.cache_data(ttl=600)
def carregar_df(conta: str) -> pd.DataFrame:
    return carregar_usuarios_df(conta)


def render_usuarios():
    st.title("👤 Usuários")

    conta = st.selectbox(
        "Conta",
        ["mania", "amazonet"],
        index=0,
    )

    try:
        with st.spinner("Carregando usuários..."):
            df = carregar_df(conta)

    except Exception as e:
        st.error("❌ Erro ao carregar usuários")
        st.exception(e)
        return

    if df.empty:
        st.warning("Nenhum usuário encontrado")
        return

    st.success(f"{len(df)} usuários carregados")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
