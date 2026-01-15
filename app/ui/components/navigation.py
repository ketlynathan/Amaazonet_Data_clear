import streamlit as st

def botao_voltar_home():
    if st.button("⬅ Voltar para Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.rerun()
