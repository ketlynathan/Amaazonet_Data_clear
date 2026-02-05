import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.relatorios.planilha_60 import read_sheet_as_dataframe


def render_planilha():
    st.title("📊 Relatório – Planilha Autônomos 60")

    # =========================
    # CARREGA DADOS
    # =========================
    with st.spinner("Carregando dados da planilha..."):
        df = read_sheet_as_dataframe()

    if df.empty:
        st.warning("A planilha não retornou dados.")
        return

    # =========================
    # NORMALIZA COLUNAS (leve)
    # =========================
    # NÃO renomeia, apenas garante string
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # =========================
    # CONVERSÃO DE DATA
    # =========================
    if "DATA DE FECHAMENTO" in df.columns:
        df["DATA DE FECHAMENTO"] = pd.to_datetime(
            df["DATA DE FECHAMENTO"],
            errors="coerce",
            dayfirst=True
        ).dt.date

    # =========================
    # SIDEBAR – FILTROS
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros")

        hoje = date.today()

        data_inicio = st.date_input(
            "📅 Data início (Fechamento)",
            value=hoje - timedelta(days=7),
        )

        data_fim = st.date_input(
            "📅 Data fim (Fechamento)",
            value=hoje,
        )

        empresa = st.multiselect(
            "🏢 Empresa",
            options=sorted(df["MANIA TELECOM"].dropna().unique())
            if "MANIA TELECOM" in df.columns else [],
        )

        tipo_venda = st.multiselect(
            "🛒 Tipo de Venda",
            options=sorted(df["A VENDA É DE UM:"].dropna().unique())
            if "A VENDA É DE UM:" in df.columns else [],
        )

        status_venda = st.multiselect(
            "📋 Status da Venda",
            options=sorted(df["AVALIAÇÃO CQ -> VENDAS"].dropna().unique())
            if "AVALIAÇÃO CQ -> VENDAS" in df.columns else [],
        )

        estado = st.multiselect(
            "📍 Estado",
            options=sorted(df["MINHA VENDA É PARA:"].dropna().unique())
            if "MINHA VENDA É PARA:" in df.columns else [],
        )

    # =========================
    # APLICA FILTROS
    # =========================
    df_f = df.copy()

    if "DATA DE FECHAMENTO" in df_f.columns:
        df_f = df_f[
            (df_f["DATA DE FECHAMENTO"] >= data_inicio)
            & (df_f["DATA DE FECHAMENTO"] <= data_fim)
        ]

    if empresa:
        df_f = df_f[df_f["MANIA TELECOM"].isin(empresa)]

    if tipo_venda:
        df_f = df_f[df_f["A VENDA É DE UM:"].isin(tipo_venda)]

    if status_venda:
        df_f = df_f[df_f["AVALIAÇÃO CQ -> VENDAS"].isin(status_venda)]

    if estado:
        df_f = df_f[df_f["MINHA VENDA É PARA:"].isin(estado)]

    from io import BytesIO

    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        try:
            import openpyxl  # garante que existe
        except ImportError:
            raise RuntimeError("openpyxl não está instalado no ambiente")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Relatorio")
        return output.getvalue()


    # =========================
    # VISUALIZAÇÃO
    # =========================
    st.dataframe(df_f, use_container_width=True)
    st.caption(f"🔢 {len(df_f)} registros filtrados")

    # =========================
    # DOWNLOAD EXCEL
    # =========================
    if not df_f.empty:
        excel_bytes = to_excel_bytes(df_f)

        st.download_button(
            label="⬇️ Baixar relatório em Excel",
            data=excel_bytes,
            file_name="relatorio_planilha_autonomos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

