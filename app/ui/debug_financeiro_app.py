import streamlit as st
import pandas as pd
from app.infra.google_sheets import read_sheet_as_dataframe


def render_debug_sheets():
    st.title("🧪 Debug Google Sheets — Auditoria Financeira")

    # ======================================================
    # 1️⃣ Relatório técnico (do sistema)
    # ======================================================
    st.subheader("📂 Relatório Técnico (df_fechamento_filtrado)")

    df_tecnico = st.session_state.get("df_fechamento_filtrado")

    if df_tecnico is None or df_tecnico.empty:
        st.warning("Relatório técnico ainda não carregado.")
    else:
        st.write("Colunas técnicas:")
        st.write({i: c for i, c in enumerate(df_tecnico.columns)})
        st.dataframe(df_tecnico.head(300), use_container_width=True)

    # ======================================================
    # 2️⃣ Planilha 51 — Auditoria Principal
    # ======================================================
    st.subheader("📄 Planilha 51 (Auditoria Principal)")

    with st.spinner("Lendo planilha 51..."):
        sheet_51 = read_sheet_as_dataframe("51")

    if sheet_51.empty:
        st.error("Planilha 51 vazia.")
    else:
        st.write("Colunas reais da 51:")
        st.write({i: c for i, c in enumerate(sheet_51.columns)})
        st.dataframe(sheet_51.head(300), use_container_width=True)

        try:
            # H = 7 | I = 8 | AH = 33
            df51_debug = sheet_51.iloc[:, [7, 8, 33]].copy()
            df51_debug.columns = ["codigo_cliente", "codigo_os", "status_51"]

            for c in df51_debug.columns:
                df51_debug[c] = df51_debug[c].astype(str).str.strip()

            st.subheader("🎯 Dados usados da Planilha 51")
            st.dataframe(df51_debug.head(300), use_container_width=True)

            st.subheader("📊 Distribuição de status (51)")
            st.dataframe(
                df51_debug["status_51"]
                .value_counts(dropna=False)
                .reset_index()
                .rename(columns={"index": "status", "status_51": "qtd"})
            )

        except Exception as e:
            st.error(f"Erro ao recortar colunas da 51: {e}")

    # ======================================================
    # 3️⃣ Planilha 60 — Fallback
    # ======================================================
    st.subheader("📄 Planilha 60 (Fallback)")

    with st.spinner("Lendo planilha 60..."):
        sheet_60 = read_sheet_as_dataframe("60")

    if sheet_60.empty:
        st.error("Planilha 60 vazia.")
    else:
        st.write("Colunas reais da 60:")
        st.write({i: c for i, c in enumerate(sheet_60.columns)})
        st.dataframe(sheet_60.head(300), use_container_width=True)

        try:
            # D = 3 | E = 4 | AF = 31
            status_af = sheet_60.iloc[:, 31] if sheet_60.shape[1] > 31 else None

            if status_af is None:
                st.error("A coluna AF (31) não existe na planilha 60.")
                return

            df60_debug = sheet_60.iloc[:, [3, 4]].copy()
            df60_debug["avaliacao_cq_instalacao"] = status_af

            df60_debug.columns = [
                "codigo_cliente",
                "codigo_os",
                "avaliacao_cq_instalacao",
            ]

            for c in df60_debug.columns:
                df60_debug[c] = df60_debug[c].astype(str).str.strip()

            st.subheader("🎯 Dados usados da Planilha 60")
            st.dataframe(df60_debug.head(300), use_container_width=True)

            st.subheader("📊 Distribuição de status (60)")
            st.dataframe(
                df60_debug["avaliacao_cq_instalacao"]
                .value_counts(dropna=False)
                .reset_index()
                .rename(columns={"index": "status", "avaliacao_cq_instalacao": "qtd"})
            )

        except Exception as e:
            st.error(f"Erro ao recortar colunas da 60: {e}")
