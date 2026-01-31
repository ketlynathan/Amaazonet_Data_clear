# app/analysis/Financeiro/financeiro_rules_venda.py
import pandas as pd
from app.analysis.Financeiro.financeiro_sources import carregar_planilhas_financeiro

def aplicar_regras_relatorio(df_base: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna DataFrame consolidado com:
    EMPRESA | CÓDIGO CLIENTE | CÓD O.S | TÉCNICO | TIPO_VENDEDOR | STATUS | FINANCEIRO | VALOR
    """
    s60, stm = carregar_planilhas_financeiro()

    # Padroniza colunas do fechamento base
    df_base = df_base.copy()
    df_base["CÓDIGO CLIENTE"] = df_base["codigo_cliente"].astype(str).str.strip()
    df_base["CÓD O.S"] = df_base["numero_ordem_servico"].astype(str).str.strip()
    df_base["EMPRESA"] = df_base.get("conta", "").str.upper()

    # Padroniza planilha 60
    s60_renamed = s60.rename(columns={
        "codigo_cliente": "CÓDIGO CLIENTE",
        "numero_ordem_servico": "CÓD O.S",
        "nome_vendedor": "TÉCNICO",
        "tipo_vendedor": "TIPO_VENDEDOR",
        "status_planilha": "STATUS"
    })
    s60_renamed["FINANCEIRO"] = s60_renamed["STATUS"].apply(
        lambda x: "PAGO" if x in ["APROVADO", "N.C APROVADO"] else "-"
    )
    s60_renamed["VALOR"] = s60_renamed["FINANCEIRO"].apply(lambda x: 50 if x == "PAGO" else 0)
    s60_renamed["EMPRESA_PLANILHA"] = "60"

    # Padroniza planilha 51_STM
    stm_renamed = stm.rename(columns={
        "codigo_cliente": "CÓDIGO CLIENTE",
        "numero_ordem_servico": "CÓD O.S",
        "nome_vendedor": "TÉCNICO",
        "tipo_vendedor": "TIPO_VENDEDOR",
        "status_planilha": "STATUS"
    })
    stm_renamed["FINANCEIRO"] = stm_renamed["STATUS"].apply(
        lambda x: "PAGO" if x in ["APROVADO", "N.C APROVADO"] else "-"
    )
    stm_renamed["VALOR"] = stm_renamed["FINANCEIRO"].apply(lambda x: 50 if x == "PAGO" else 0)
    stm_renamed["EMPRESA_PLANILHA"] = "51_STM"

    # Concatena planilhas
    planilhas = pd.concat([s60_renamed, stm_renamed], ignore_index=True)

    # Merge com fechamento
    df_relatorio = df_base.merge(
        planilhas,
        on=["CÓDIGO CLIENTE", "CÓD O.S"],
        how="left",
        suffixes=("", "_planilha")
    )

    # Preenche OS não encontradas
    df_relatorio["STATUS"].fillna("-", inplace=True)
    df_relatorio["FINANCEIRO"].fillna("-", inplace=True)
    df_relatorio["VALOR"].fillna(0, inplace=True)
    df_relatorio["TIPO_VENDEDOR"].fillna("-", inplace=True)

    # Ordena e index sequencial
    df_relatorio = df_relatorio.sort_values(["EMPRESA", "CÓDIGO CLIENTE", "CÓD O.S"]).reset_index(drop=True)
    df_relatorio.index = df_relatorio.index + 1

    return df_relatorio
