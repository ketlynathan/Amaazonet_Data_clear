import streamlit as st
import pandas as pd
from app.analysis.google_sheets import read_sheet_as_dataframe


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
    # 3️⃣ Planilha 60 — Fallback (Principal)
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
            if sheet_60.shape[1] <= 31:
                st.error("A coluna AF (31) não existe na planilha 60.")
            else:
                df60_debug = sheet_60.iloc[:, [3, 4, 31]].copy()
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


    # ======================================================
    # 3️⃣ Planilha 60 — Aba Secundária (Vendas)
    # ======================================================
    st.subheader("📄 Planilha 60 (Aba Secundária - ANÁLISE E CADASTRO)")

    with st.spinner("Lendo planilha 60 (vendas)..."):
        # Lendo a partir da linha 11218
        sheet_60_venda = read_sheet_as_dataframe("60_venda", start_row=11218)

    if sheet_60_venda.empty:
        st.error("Planilha 60 (vendas) vazia.")
    else:
        st.write("Colunas reais da 60 (vendas):")
        st.write({i: c for i, c in enumerate(sheet_60_venda.columns)})
        st.dataframe(sheet_60_venda.head(300), use_container_width=True)

        try:
            # D = 3 | E = 4 | Y = 24
            if sheet_60_venda.shape[1] <= 25:
                st.error("A coluna Y (24) não existe na planilha 60_venda.")
            else:
                # Selecionar colunas desejadas
                df60_venda_debug = sheet_60_venda.iloc[:, [0, 1, 4, 5, 6, 10]].copy()

                df60_venda_debug.columns = [
                    "status_analise",
                    "vendedor",
                    "cod_cliente",
                    "cod_os",
                    "empresa",   # MANIA TELECOM
                    "tipo_venda", # A VENDA É DE UM:
                ]

                # ✅ limpar valores corretamente
                for c in df60_venda_debug.columns:
                    df60_venda_debug[c] = df60_venda_debug[c].astype(str).str.strip()

                st.subheader("🎯 Dados usados da Planilha 60 (Vendas)")
                st.dataframe(df60_venda_debug.head(300), use_container_width=True)

                st.subheader("📊 Distribuição por Vendedor")
                st.dataframe(
                    df60_venda_debug["vendedor"]
                    .value_counts(dropna=False)
                    .reset_index()
                    .rename(columns={"index": "vendedor", "vendedor": "qtd"})
                )

        except Exception as e:
            st.error(f"Erro ao recortar colunas da 60_venda: {e}")


        
    read_sheet_as_dataframe("51_STM")
    # ======================================================
    # 4️⃣ Planilha 51_STM — Auditoria Complementar
    # ======================================================
    st.subheader("📄 Planilha 51_STM (Auditoria Complementar)")

    with st.spinner("Lendo planilha 51_STM..."):
        sheet_stm = read_sheet_as_dataframe("51_STM")

    if sheet_stm.empty:
        st.error("Planilha 51_STM vazia.")
    else:
        st.write("Colunas reais da 51_STM:")
        st.write({i: c for i, c in enumerate(sheet_stm.columns)})
        st.dataframe(sheet_stm.head(300), use_container_width=True)

        try:
            # AJUSTE OS ÍNDICES SE NECESSÁRIO APÓS VER AS COLUNAS
            df_stm_debug = sheet_stm.iloc[:, [2, 3, 33]].copy()

            df_stm_debug.columns = [
                "codigo_cliente",
                "codigo_os",
                "status_51_stm",
            ]

            for c in df_stm_debug.columns:
                df_stm_debug[c] = df_stm_debug[c].astype(str).str.strip()

            st.subheader("🎯 Dados usados da 51_STM")
            st.dataframe(df_stm_debug.head(300), use_container_width=True)

            st.subheader("📊 Distribuição de status (51_STM)")
            st.dataframe(
                df_stm_debug["status_51_stm"]
                .value_counts(dropna=False)
                .reset_index()
                .rename(columns={"index": "status", "status_51_stm": "qtd"})
            )

        except Exception as e:
            st.error(f"Erro ao recortar colunas da 51_STM: {e}")

    # ======================================================
    # 4️⃣ Planilha 39 — Agendamento e Financeiro
    # ======================================================
    st.subheader("📄 Planilha 39 (Agendamento e Financeiro)")

    with st.spinner("Lendo planilha 39..."):
        sheet_39 = read_sheet_as_dataframe("39")

    if sheet_39.empty:
        st.error("Planilha 39 vazia.")
    else:
        st.write("Colunas reais da 39:")
        st.write({i: c for i, c in enumerate(sheet_39.columns)})
        st.dataframe(sheet_39.head(300), use_container_width=True)

        try:
            # D = 3 | E = 4
            if sheet_39.shape[1] < 5:
                st.error("A Planilha 39 não possui colunas suficientes (esperado D e E).")
                return

            df39_debug = sheet_39.iloc[:, [3, 4]].copy()
            df39_debug.columns = [
                "codigo_cliente",
                "codigo_os",
            ]

            for c in df39_debug.columns:
                df39_debug[c] = df39_debug[c].astype(str).str.strip()

            st.subheader("🎯 Dados usados da Planilha 39")
            st.dataframe(df39_debug.head(300), use_container_width=True)

            st.subheader("📊 Quantidade de registros válidos (39)")
            st.write(f"Total linhas com cliente/OS: {len(df39_debug)}")

        except Exception as e:
            st.error(f"Erro ao recortar colunas da 39: {e}")


