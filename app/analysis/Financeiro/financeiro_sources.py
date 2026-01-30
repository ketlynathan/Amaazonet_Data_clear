from app.analysis.google_sheets import read_sheet_as_dataframe

def carregar_planilhas_financeiro():
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")

    # ================= PLANILHA 60 =================
    s60 = sheet_60.iloc[:, [1, 3, 4, 7, 21]].copy()
    s60.columns = [
        "nome_vendedor",          # B
        "codigo_cliente",         # D
        "numero_ordem_servico",   # E
        "tipo_vendedor",          # H
        "status_planilha"         # V
    ]
    s60["origem"] = "60"

    # ================= PLANILHA STM =================
    stm = sheet_51_stm.iloc[276:, [2, 3, 5, 10, 23]].copy()
    stm.columns = [
        "codigo_cliente",         # C
        "numero_ordem_servico",   # D
        "nome_vendedor",          # F
        "tipo_vendedor",          # K
        "status_planilha"         # X
    ]
    stm["origem"] = "51_STM"

    # ================= PADRONIZAÇÃO =================
    for df in (s60, stm):
        df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip().str.upper()
        df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip().str.upper()
        df["nome_vendedor"] = df["nome_vendedor"].astype(str).str.strip()
        df["tipo_vendedor"] = df["tipo_vendedor"].astype(str).str.strip().str.upper()
        df["status_planilha"] = df["status_planilha"].astype(str).str.strip().str.upper()

    return s60, stm
