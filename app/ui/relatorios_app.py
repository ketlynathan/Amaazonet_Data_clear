import streamlit as st
from datetime import date, timedelta

from app.analysis.relatorios.vendas import relatorio_vendas_df
# from app.analysis.relatorios.instalacao_tecnica import relatorio_instalacao_tecnica_df
# from app.analysis.relatorios.comissoes import relatorio_comissoes_df


def render_relatorios():
    st.title("📈 Relatórios")

    # ======================================================
    # FILTROS (SIDEBAR)
    # ======================================================
    with st.sidebar:
        st.subheader("Filtros do Relatório")

        tipo = st.radio(
            "Tipo de relatório",
            [
                "Vendas",
                "Comissões 🚧",
                # "Instalação Técnica 🚧",
            ],
        )

        periodicidade = st.radio(
            "Período",
            ["Semanal", "Mensal", "Período livre"],
        )

        hoje = date.today()

        if periodicidade == "Semanal":
            data_inicio = hoje - timedelta(days=7)
            data_fim = hoje

        elif periodicidade == "Mensal":
            data_inicio = hoje.replace(day=1)
            data_fim = hoje

        else:
            data_inicio = st.date_input("Data início", value=hoje - timedelta(days=7))
            data_fim = st.date_input("Data fim", value=hoje)

        st.divider()

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania"],
        )

        gerar = st.button("📊 Gerar relatório", use_container_width=True)

    # ======================================================
    # CONTROLE DE ESTADO (Streamlit não perder resultado)
    # ======================================================
    if "df_relatorio" not in st.session_state:
        st.session_state.df_relatorio = None

    if "tipo_relatorio" not in st.session_state:
        st.session_state.tipo_relatorio = None

    # ======================================================
    # BOTÃO GERAR
    # ======================================================
    if gerar:
        # 🔴 Relatórios fora do ar
        if "🚧" in tipo:
            st.warning(
                "🚧 Este relatório ainda está fora do ar.\n\n"
                "Estamos finalizando as regras de negócio e validações antes de liberar."
            )
            st.session_state.df_relatorio = None
            return

        with st.spinner("Gerando relatório..."):
            if tipo == "Vendas":
                df = relatorio_vendas_df(contas, data_inicio, data_fim)

            else:
                st.warning("Relatório ainda não implementado.")
                return

        st.session_state.df_relatorio = df
        st.session_state.tipo_relatorio = tipo

    # ======================================================
    # EXIBIÇÃO DO RESULTADO
    # ======================================================
    df = st.session_state.df_relatorio
    tipo_salvo = st.session_state.tipo_relatorio

    if df is None:
        st.info("Selecione os filtros e clique em **Gerar relatório**")
        return

    if df.empty:
        st.warning("Nenhum registro encontrado para o período selecionado.")
        return

    st.success(f"✅ {len(df)} registros encontrados — {tipo_salvo}")

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Exportar CSV",
        df.to_csv(index=False),
        file_name=f"relatorio_{tipo_salvo.lower()}.csv",
        mime="text/csv",
        use_container_width=True,
    )
