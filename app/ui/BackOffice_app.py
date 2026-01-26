import streamlit as st
import pandas as pd
from datetime import date
from app.analysis.google_sheets import read_sheet_as_dataframe

def render_60_vendas():
    """
    Renderiza a aba de vendas da Planilha 60 com filtros laterais
    e gráficos de distribuição por vendedor e back.
    """

    st.subheader("📄 Planilha 60 (Vendas) - ANÁLISE E CADASTRO")

    # =========================
    # Leitura da aba a partir da linha 11218
    # =========================
    with st.spinner("Lendo planilha 60 (vendas)..."):
        sheet_60_venda = read_sheet_as_dataframe("60_venda", start_row=11218)

    if sheet_60_venda.empty:
        st.error("Planilha 60 (vendas) vazia.")
        return

    # ------------------------------
    # Selecionar colunas de interesse
    # ------------------------------
    df60_venda_debug = sheet_60_venda.iloc[:, [0, 1, 4, 5, 6, 10]].copy()
    df60_venda_debug.columns = [
        "status_analise",
        "vendedor",
        "cod_cliente",
        "cod_os",
        "empresa",
        "tipo_venda",
    ]

    # Limpar valores
    for c in df60_venda_debug.columns:
        df60_venda_debug[c] = df60_venda_debug[c].astype(str).str.strip()

    # ------------------------------
    # Adicionar colunas auxiliares
    # ------------------------------
    df60_venda_debug["back"] = sheet_60_venda.iloc[:, 3].astype(str).str.strip()  # coluna D original
    df60_venda_debug["data_fechamento"] = pd.to_datetime(sheet_60_venda.iloc[:, 7], errors="coerce")  # coluna 7 = Data termino

    # =========================
    # Sidebar de filtros
    # =========================
    with st.sidebar:
        st.subheader("🎛️ Filtros de Vendas")

        # Filtro por empresa
        empresas = sorted(df60_venda_debug["empresa"].dropna().unique())
        selected_empresas = st.multiselect(
            "Empresa",
            empresas,
            default=empresas
        )

        # Filtro por Back
        back_options = ["Todos"] + sorted(df60_venda_debug["back"].dropna().unique())
        selected_back = st.selectbox("Back", back_options)

        # Filtro período
        min_date = df60_venda_debug["data_fechamento"].min().date()
        max_date = df60_venda_debug["data_fechamento"].max().date()
        data_inicio = st.date_input("Data início (fechamento)", min_value=min_date, max_value=max_date, value=min_date)
        data_fim = st.date_input("Data fim (fechamento)", min_value=min_date, max_value=max_date, value=max_date)

    # =========================
    # Aplicar filtros
    # =========================
    df_filtrado = df60_venda_debug.copy()

    if selected_empresas:
        df_filtrado = df_filtrado[df_filtrado["empresa"].isin(selected_empresas)]

    if selected_back != "Todos":
        df_filtrado = df_filtrado[df_filtrado["back"] == selected_back]

    df_filtrado = df_filtrado[
        (df_filtrado["data_fechamento"].dt.date >= data_inicio) &
        (df_filtrado["data_fechamento"].dt.date <= data_fim)
    ]

    # =========================
    # Mostrar resultados
    # =========================
    st.success(f"✅ {len(df_filtrado)} vendas encontradas")
    st.dataframe(df_filtrado, use_container_width=True)

    # ------------------------------
    # Distribuição por Vendedor
    # ------------------------------
    st.subheader("📊 Distribuição por Vendedor")
    df_vendedor_count = df_filtrado["vendedor"].value_counts(dropna=False).reset_index()
    df_vendedor_count.columns = ["vendedor", "qtd"]
    st.bar_chart(df_vendedor_count.set_index("vendedor"))

    # ------------------------------
    # Distribuição por Back (Gráfico de barras)
    # ------------------------------
    st.subheader("📊 Distribuição por Back")
    df_back_count = df_filtrado["back"].value_counts(dropna=False).reset_index()
    df_back_count.columns = ["back", "qtd"]
    st.bar_chart(df_back_count.set_index("back"))
