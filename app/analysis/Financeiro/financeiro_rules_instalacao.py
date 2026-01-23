import pandas as pd
import streamlit as st
from app.analysis.google_sheets import read_sheet_as_dataframe


# ======================================================
# Carrega planilhas Google
# ======================================================
@st.cache_data(ttl=600)
def carregar_planilhas():
    sheet_51 = read_sheet_as_dataframe("51")
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")
    return sheet_51, sheet_60, sheet_51_stm


# ======================================================
# Função principal
# ======================================================
def aplicar_regras_financeiras(df: pd.DataFrame) -> pd.DataFrame:
    sheet_51, sheet_60, sheet_51_stm = carregar_planilhas()

    # ======================================================
    # 1️⃣ Normaliza HUBSOFT
    # ======================================================
    df = df.copy()
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip()
    df["usuario_fechamento"] = df["usuario_fechamento"].astype(str)

    # ======================================================
    # 2️⃣ Normaliza Planilha 51
    # H (7) Cliente | I (8) OS | AH (33) Status
    # ======================================================
    sheet_51 = sheet_51.iloc[:, [7, 8, 33]].copy()
    sheet_51.columns = ["codigo_cliente", "numero_ordem_servico", "status_51"]

    for c in sheet_51.columns:
        sheet_51[c] = sheet_51[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 3️⃣ Normaliza Planilha 51_STM
    # C (2) Cliente | D (3) OS | AH (33) Status
    # ======================================================
    sheet_51_stm = sheet_51_stm.iloc[:, [2, 3, 33]].copy()
    sheet_51_stm.columns = ["codigo_cliente", "numero_ordem_servico", "status_51_stm"]

    for c in sheet_51_stm.columns:
        sheet_51_stm[c] = sheet_51_stm[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 4️⃣ Normaliza Planilha 60
    # D (3) Cliente | E (4) OS | AE (30) ou AF (31) Status
    # ======================================================
    status_60 = sheet_60.iloc[:, 30]

    if sheet_60.shape[1] > 31:
        status_alt = sheet_60.iloc[:, 31]
        status_60 = status_60.fillna(status_alt)

    sheet_60 = sheet_60.iloc[:, [3, 4]].copy()
    sheet_60["status_60"] = status_60

    sheet_60.columns = ["codigo_cliente", "numero_ordem_servico", "status_60"]

    for c in sheet_60.columns:
        sheet_60[c] = sheet_60[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 5️⃣ Merge
    # ======================================================
    df = df.merge(sheet_51, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df = df.merge(sheet_60, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df = df.merge(sheet_51_stm, on=["codigo_cliente", "numero_ordem_servico"], how="left")

    # ======================================================
    # 6️⃣ Regra NADINEI
    # ======================================================
    def status_auditoria(row):
        tecnico = str(row["usuario_fechamento"]).upper()

        if "NADINEI" in tecnico:
            if pd.notna(row["status_51_stm"]):
                return row["status_51_stm"]
            return ""

        if pd.notna(row["status_51"]):
            return row["status_51"]
        if pd.notna(row["status_60"]):
            return row["status_60"]

        return ""
    df["status_auditoria"] = df.apply(status_auditoria, axis=1)

    # ======================================================
    # 7️⃣ Status financeiro
    # ======================================================
    def status_financeiro(status):
        status = str(status).upper()
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    # ======================================================
    # 8️⃣ Valor por técnico
    # ======================================================
    def valor_por_tecnico(nome):
        nome = str(nome).upper()
        if "LOBATOS" in nome:
            return 90
        if "EDINELSON" in nome:
            return 50
        if "NADINEI" in nome:
            return 60
        return 0

    df["valor_base"] = df["usuario_fechamento"].apply(valor_por_tecnico)

    df["valor_a_pagar"] = df.apply(
        lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0,
        axis=1,
    )

    # ======================================================
    # 9️⃣ ID
    # ======================================================
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df
