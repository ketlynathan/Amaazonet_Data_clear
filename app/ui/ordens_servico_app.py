import streamlit as st
from app.analysis.ordens_servico import carregar_ordens_servico_df


@st.cache_data(ttl=300)
def carregar_df(conta, data_inicio, data_fim, tipo_data):
    return carregar_ordens_servico_df(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data=tipo_data,
    )


def render_ordens_servico():
    st.title("🛠️ Ordens de Serviço")

    with st.sidebar:
        st.subheader("Filtros")

        conta = st.selectbox("Conta", ["mania", "amazonet"])
        tipo_data = st.selectbox(
            "Tipo de data",
            [
                "data_cadastro",
                "data_inicio_programado",
                "data_inicio_executado",
                "data_termino_executado",
            ],
        )

        data_inicio = st.date_input("Data início")
        data_fim = st.date_input("Data fim")

    with st.spinner("Carregando ordens de serviço..."):
        df = carregar_df(
            conta,
            data_inicio,
            data_fim,
            tipo_data,
        )

    st.success(f"{len(df)} ordens encontradas")
    st.dataframe(df, use_container_width=True)
