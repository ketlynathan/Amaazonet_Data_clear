import pandas as pd
from app.infra.google_sheets import read_sheet_as_dataframe


def aplicar_regras_financeiras(df_base: pd.DataFrame) -> pd.DataFrame:
    df = df_base.copy()

    # ======================================================
    # 1️⃣ Lê as duas planilhas
    # ======================================================
    sheet_51 = read_sheet_as_dataframe("51")
    sheet_60 = read_sheet_as_dataframe("60")

    # ======================================================
    # 2️⃣ Normaliza planilha 51
    # Colunas: H (7) = Cliente | I (8) = OS | AH (33) = Status
    # ======================================================
    sheet_51 = sheet_51.iloc[:, [7, 8, 33]]
    sheet_51.columns = ["codigo_cliente", "numero_ordem_servico", "status_51"]

    sheet_51["codigo_cliente"] = sheet_51["codigo_cliente"].astype(str).str.strip()
    sheet_51["numero_ordem_servico"] = sheet_51["numero_ordem_servico"].astype(str).str.strip()
    sheet_51["status_51"] = sheet_51["status_51"].astype(str).str.upper().str.strip()

    # ======================================================
    # 3️⃣ Normaliza planilha 60
    # Colunas:
    # D (3) = Cliente
    # E (4) = OS
    # AE (30) ou AF (31) = Status
    # ======================================================
    # Tentamos AE primeiro, se vier vazio usamos AF
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
    # 4️⃣ Normaliza o dataframe técnico
    # ======================================================
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip()
    df["usuario_fechamento"] = df["usuario_fechamento"].astype(str)

    # ======================================================
    # 5️⃣ Merge primeiro com a 51
    # ======================================================
    df = df.merge(
        sheet_51,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left"
    )

    # ======================================================
    # 6️⃣ Para os que não acharam na 51, tenta na 60
    # ======================================================
    df = df.merge(
        sheet_60,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left"
    )

    # Se existir na 51 usa ela, senão usa a 60
    df["status_auditoria"] = df["status_51"].fillna(df["status_60"])

    # ======================================================
    # 7️⃣ STATUS FINANCEIRO
    # ======================================================
    def status_financeiro(status):
        if not status:
            return "-"
        
        status = str(status).upper().strip()

        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"

        if status in ["REPROVADO", "REPROVADO PARCIAL"]:
            return "-"

        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    # ======================================================
    # 8️⃣ Valor por técnico
    # ======================================================
    def valor_por_tecnico(nome):
        nome = nome.upper()

        if "LOBATOS" in nome:
            return 90
        if "EDINELSON" in nome:
            return 50
        if "NADINEI" in nome:
            return 60
        return 0

    df["valor_base"] = df["usuario_fechamento"].apply(valor_por_tecnico)

    # Só paga se status for PAGO
    df["valor_a_pagar"] = df.apply(
    lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else "-",
    axis=1
)

    # ======================================================
    # 9️⃣ ID incremental
    # ======================================================
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df
