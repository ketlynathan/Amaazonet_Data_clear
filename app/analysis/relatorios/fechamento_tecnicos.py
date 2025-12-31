from datetime import date
from typing import List
import pandas as pd

from app.analysis.ordens_servico import carregar_ordens_servico_df


def relatorio_fechamento_tecnicos_df(
    contas: List[str],
    data_inicio: date,
    data_fim: date,
    estados: List[str],
) -> pd.DataFrame:
    """
    Retorna TODAS as ordens de serviço fechadas no período,
    para todas as contas e estados informados.
    """

    dfs: list[pd.DataFrame] = []
    estados_upper = [e.upper() for e in estados]

    for conta in contas:
        df = carregar_ordens_servico_df(
            conta=conta,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo_data="data_termino_executado",
        )

        if df.empty:
            continue

        # Filtro por estado
        if "dados_endereco_instalacao.estado" in df.columns:
            df = df[
                df["dados_endereco_instalacao.estado"]
                .astype(str)
                .str.upper()
                .isin(estados_upper)
            ]

        df["conta"] = conta.upper()
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs, ignore_index=True)

    return df_final
