from app.analysis.google_sheets import read_sheet_as_dataframe
from app.analysis.Financeiro.financeiro_utils import padronizar_campos_chave


def carregar_planilhas_financeiro():
    sheet_51 = read_sheet_as_dataframe("51")
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")

    # Seleciona e padroniza colunas
    s51 = sheet_51.iloc[:, [7, 8, 3, 24]].copy()
    s51.columns = ["codigo_cliente", "numero_ordem_servico", "info_51", "status_51"]
    s51 = padronizar_campos_chave(s51)

    s60 = sheet_60.iloc[:, [1, 3, 4, 7, 21]].copy()
    s60.columns = [
        "nome_vendedor",
        "codigo_cliente",
        "numero_ordem_servico",
        "tipo_vendedor",
        "status_60"
    ]

    # Padroniza campos chave
    s60["codigo_cliente"] = s60["codigo_cliente"].astype(str).str.strip().str.upper()
    s60["numero_ordem_servico"] = s60["numero_ordem_servico"].astype(str).str.strip().str.upper()

    # Padroniza texto do tipo
    s60["tipo_vendedor"] = s60["tipo_vendedor"].astype(str).str.strip().str.upper()
    s60["nome_vendedor"] = s60["nome_vendedor"].astype(str).str.strip()

    s60_autonomo = s60[s60["tipo_vendedor"] == "VENDEDOR AUTÔNOMO"].copy()

    return s51, s60, s60_autonomo



    stm = sheet_51_stm.iloc[:, [2, 3, 10, 23]].copy()
    stm.columns = ["codigo_cliente", "numero_ordem_servico", "info_51_stm", "status_51_stm"]
    stm = padronizar_campos_chave(stm)

    return s51, s60, stm
