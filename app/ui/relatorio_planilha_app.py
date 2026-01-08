# app/ui/relatorio_planilha_app.py
import streamlit as st
import pandas as pd

from app.infra.google_sheets import read_sheet_as_dataframe


def render_planilha():
    st.title("📊 Relatório – Planilha Google")

    with st.spinner("Carregando dados da planilha..."):
        df = read_sheet_as_dataframe()

    if df.empty:
        st.warning("A planilha não retornou dados.")
        return

    # --- Filtros dinâmicos (opcional, mas poderoso)
    with st.expander("🔍 Filtros", expanded=False):
        columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Selecione colunas para exibição",
            options=columns,
            default=columns,
        )

    df_view = df[selected_columns] if selected_columns else df

    st.dataframe(df_view, use_container_width=True)

    st.caption(f"{len(df_view)} registros carregados")
