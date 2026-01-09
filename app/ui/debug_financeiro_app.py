import streamlit as st
from app.infra.google_sheets import read_sheet_as_dataframe

def render_debug_sheets():
    st.title("🧪 Debug Google Sheets — Auditoria Financeira")

    with st.spinner("Lendo planilha do Google..."):
        df = read_sheet_as_dataframe()

    if df.empty:
        st.error("A planilha retornou vazia.")
        return

    st.subheader("📄 Colunas recebidas (índice real)")
    st.write({i: col for i, col in enumerate(df.columns)})

    # ==============================
    # Seleção por ÍNDICE REAL
    # ==============================
    try:
        df_debug = df.iloc[:, [7, 8, 33, 34]].copy()
        df_debug.columns = [
            "codigo_cliente",
            "codigo_os",
            "AG_COL_34",
            "AH_STATUS",
        ]
    except Exception as e:
        st.error(f"Erro ao selecionar colunas: {e}")
        return

    # Limpeza básica
    for c in df_debug.columns:
        df_debug[c] = df_debug[c].astype(str).str.strip()

    st.subheader("📋 Dados reais usados na auditoria")
    st.dataframe(df_debug.head(300), use_container_width=True)

    # ==============================
    # Estatística do status
    # ==============================
    st.subheader("📊 Distribuição de Status Financeiro (COL_35)")

    st.dataframe(
        df_debug["AH_STATUS"]
        .value_counts(dropna=False)
        .reset_index()
        .rename(columns={"index": "status", "AH_STATUS": "qtd"})
    )
