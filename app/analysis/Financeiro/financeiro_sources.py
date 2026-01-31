# app/analysis/Financeiro/financeiro_sources.py
import pandas as pd
from app.analysis.google_sheets import read_sheet_as_dataframe

def carregar_planilhas_financeiro():
    """
    Carrega as planilhas 60 e 51_STM e retorna DataFrames padronizados
    """
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")

    # ================= PLANILHA 60 =================
    s60 = sheet_60.iloc[:, [1, 3, 4, 7, 21]].copy()
    s60.columns = [
        "nome_vendedor",
        "codigo_cliente",
        "numero_ordem_servico",
        "tipo_vendedor",
        "status_planilha"
    ]
    s60["origem"] = "60"

    # ================= PLANILHA STM =================
    stm = sheet_51_stm.iloc[276:, [2, 3, 5, 10, 23]].copy()
    stm.columns = [
        "codigo_cliente",
        "numero_ordem_servico",
        "nome_vendedor",
        "tipo_vendedor",
        "status_planilha"
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
