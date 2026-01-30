from datetime import date
from typing import List
import pandas as pd



import pandas as pd


def relatorio_fechamento_retirada_df(df_metabase: pd.DataFrame) -> pd.DataFrame:
    """
    Trata os dados de fechamento de retiradas vindos do Metabase.
    NÃO consulta HubSoft.
    NÃO usa conta.
    NÃO chama API.
    """

    if df_metabase is None or df_metabase.empty:
        return pd.DataFrame()

    df = df_metabase.copy()

    # =========================
    # GARANTE COLUNAS IMPORTANTES
    # =========================
    colunas_necessarias = [
        "numero_ordem_servico",
        "usuario_fechamento",
        "tipo_ordem_servico",
        "data_termino_executado",
        "nome_cliente",
        "cidade",
        "bairro",
        "codigo_cliente",
        "motivo_fechamento",
    ]

    for col in colunas_necessarias:
        if col not in df.columns:
            df[col] = None

    # =========================
    # GARANTE QUE É OS FECHADA
    # =========================
    df = df[df["data_termino_executado"].notna()]

    # =========================
    # CONVERSÃO DE DATA
    # =========================
    df["data_termino_executado"] = pd.to_datetime(
        df["data_termino_executado"],
        dayfirst=True,
        errors="coerce",
    )

    return df
