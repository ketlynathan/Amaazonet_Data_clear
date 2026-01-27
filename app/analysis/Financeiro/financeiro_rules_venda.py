import pandas as pd
from app.analysis.Financeiro.financeiro_sources import carregar_planilhas_financeiro
from app.analysis.Financeiro.financeiro_utils import padronizar_campos_chave


def aplicar_regras(df_base: pd.DataFrame) -> dict:
    df_base = padronizar_campos_chave(df_base)

    s51, s60, stm = carregar_planilhas_financeiro()

    # Cruzamentos
    df_stm = df_base.merge(stm, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df_51 = df_base.merge(s51, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df_60 = df_base.merge(s60, on=["codigo_cliente", "numero_ordem_servico"], how="left")

    # Regra de classificação
    resumo = pd.DataFrame({
        "codigo_cliente": df_base["codigo_cliente"],
        "numero_ordem_servico": df_base["numero_ordem_servico"],
        "encontrado_51_stm": df_stm["status_51_stm"].notna(),
        "encontrado_51": df_51["status_51"].notna(),
        "encontrado_60": df_60["status_60"].notna(),
    })

    resumo["origem_encontrada"] = (
        resumo["encontrado_51_stm"].map({True: "51_STM", False: ""}) +
        resumo["encontrado_51"].map({True: " 51", False: ""}) +
        resumo["encontrado_60"].map({True: " 60", False: ""})
    ).str.strip()

    return {
        "base": df_base,
        "51_STM": df_stm,
        "51": df_51,
        "60": df_60,
        "resumo": resumo
    }
