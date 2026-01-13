import pandas as pd
import streamlit as st
from app.infra.google_sheets import read_sheet_as_dataframe


@st.cache_data(ttl=600)
def carregar_planilhas():
    sheet_51 = read_sheet_as_dataframe("51")
    sheet_60 = read_sheet_as_dataframe("60")
    return sheet_51, sheet_60


def aplicar_regras_financeiras(df_base: pd.DataFrame) -> pd.DataFrame:
    df = df_base.copy()

    # ======================================================
    # 1️⃣ Carrega planilhas
    # ======================================================
    sheet_51, sheet_60 = carregar_planilhas()

    # ======================================================
    # 2️⃣ Normaliza planilha 51
    # H (7) = Cliente | I (8) = OS | AH (33) = Status
    # ======================================================
    sheet_51 = sheet_51.iloc[:, [7, 8, 33]].copy()
    sheet_51.columns = ["codigo_cliente", "numero_ordem_servico", "status_51"]

    sheet_51["codigo_cliente"] = sheet_51["codigo_cliente"].astype(str).str.strip()
    sheet_51["numero_ordem_servico"] = sheet_51["numero_ordem_servico"].astype(str).str.strip()
    sheet_51["status_51"] = sheet_51["status_51"].astype(str).str.upper().str.strip()

    # ======================================================
    # 3️⃣ Normaliza planilha 60
    # D (3) = Cliente | E (4) = OS | AE (30) ou AF (31) = Status
    # ======================================================
    sheet_60 = sheet_60.copy()
    sheet_60["status_60"] = sheet_60.iloc[:, 30]

    if sheet_60.shape[1] > 31:
        sheet_60["status_alt"] = sheet_60.iloc[:, 31]
        sheet_60["status_60"] = sheet_60["status_60"].fillna(sheet_60["status_alt"])

    sheet_60 = sheet_60.iloc[:, [3, 4]].assign(status_60=sheet_60["status_60"])
    sheet_60.columns = ["codigo_cliente", "numero_ordem_servico", "status_60"]

    sheet_60["codigo_cliente"] = sheet_60["codigo_cliente"].astype(str).str.strip()
    sheet_60["numero_ordem_servico"] = sheet_60["numero_ordem_servico"].astype(str).str.strip()
    sheet_60["status_60"] = sheet_60["status_60"].astype(str).str.upper().str.strip()

    # ======================================================
    # 4️⃣ Normaliza dataframe técnico
    # ======================================================
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip()
    df["usuario_fechamento"] = df["usuario_fechamento"].astype(str)

    


    # ======================================================
    # 5️⃣ Merge com a 51
    # ======================================================
    df = df.merge(
        sheet_51,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left",
    )

    # ======================================================
    # 6️⃣ Merge com a 60
    # ======================================================
    df = df.merge(
        sheet_60,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left",
    )

    # ======================================================
    # 7️⃣ Status auditoria
    # ======================================================
    df["status_auditoria"] = df["status_51"].fillna(df["status_60"]).fillna("")

    # ======================================================
    # 8️⃣ Status financeiro
    # ======================================================
    def status_financeiro(status):
        status = str(status).upper().strip()
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    # ======================================================
    # 9️⃣ Valor por técnico
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
    # 🔟 ID incremental
    # ======================================================
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df
