import pandas as pd
from app.analysis.Financeiro.calculo_comissao import buscar_valor_meta

def gerar_relatorio_producao_instalacao(df, regiao="AM"):
    resumo = (
        df.groupby("usuario_fechamento")
        .size()
        .reset_index(name="TOTAL_OS")
    )

    resumo["VALOR_UNITARIO"] = resumo["TOTAL_OS"].apply(
        lambda qtd: buscar_valor_meta("PRODUCAO_INSTALACAO", regiao, qtd)
    )

    resumo["VALOR_A_RECEBER"] = resumo["TOTAL_OS"] * resumo["VALOR_UNITARIO"]

    return resumo.sort_values("TOTAL_OS", ascending=False)
