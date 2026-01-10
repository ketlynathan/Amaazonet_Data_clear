import pandas as pd
from app.infra.google_sheets import read_sheet_as_dataframe


def aplicar_regras_financeiras(df_base: pd.DataFrame) -> pd.DataFrame:
    df = df_base.copy()

    # ===============================
    # 1) Lê a planilha do Google
    # ===============================
    sheet = read_sheet_as_dataframe()

    # Mantém apenas as colunas necessárias
    sheet = sheet.iloc[:, [7, 8, 33]]  # Código Cliente, Código OS, Status
    sheet.columns = ["codigo_cliente", "numero_ordem_servico", "status_auditoria"]

    # Normaliza
    sheet["codigo_cliente"] = sheet["codigo_cliente"].astype(str).str.strip()
    sheet["numero_ordem_servico"] = sheet["numero_ordem_servico"].astype(str).str.strip()
    sheet["status_auditoria"] = sheet["status_auditoria"].astype(str).str.upper().str.strip()

    # ===============================
    # 2) Normaliza o dataframe técnico
    # ===============================
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip()
    df["usuario_fechamento"] = df["usuario_fechamento"].astype(str)

    # ===============================
    # 3) Merge técnico × auditoria
    # ===============================
    df = df.merge(
        sheet,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left"
    )

    # ===============================
    # 4) STATUS FINANCEIRO
    # ===============================
    def status_financeiro(status):
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)
    

    # ===============================
    # 5) Valor por técnico
    # ===============================
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
        lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0,
        axis=1
    )
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df