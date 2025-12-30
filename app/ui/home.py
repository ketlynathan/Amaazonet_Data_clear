import streamlit as st


def render_home():
    st.title("📊 HubSoft Analytics")

    st.markdown(
        """
        Bem-vindo ao **HubSoft Analytics** 🚀  

        Use o menu lateral para navegar entre:
        - 👤 Usuários
        - 🛠️ Ordens de Serviço
        - 📈 Relatórios
        """
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Status", "Conectado")
    col2.metric("API", "HubSoft")
    col3.metric("Ambiente", "Produção")
