from datetime import date
from typing import List
import pandas as pd

from app.analysis.ordens_servico import carregar_ordens_servico_df
from app.analysis.relatorios.fechamento_venda import relatorio_fechamento_venda_df

def relatorio_fechamento_venda_df(
    contas: List[str],
    data_inicio: date,
    data_fim: date,
    estados: List[str],
) -> pd.DataFrame:
    """
    Retorna ordens de serviço com término executado no período,
    respeitando contas e estados (modelo real HubSoft).
    """

    dfs: list[pd.DataFrame] = []

    estados_upper = [
        e.strip().upper()
        for e in estados
        if isinstance(e, str) and e.strip()
    ]

    for conta in contas:
        df = carregar_ordens_servico_df(
            conta=conta,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo_data="data_termino_executado",
        )

        if df is None or df.empty:
            continue

        # =========================
        # GARANTIA DE FECHAMENTO
        # =========================
        if "data_termino_executado" in df.columns:
            df = df[df["data_termino_executado"].notna()]

        # =========================
        # FILTRO DE ESTADO (SE EXISTIR)
        # =========================
        if estados_upper and "dados_endereco_instalacao.estado" in df.columns:
            df["dados_endereco_instalacao.estado"] = (
                df["dados_endereco_instalacao.estado"]
                .astype(str)
                .str.upper()
            )

            df = df[
                df["dados_endereco_instalacao.estado"]
                .isin(estados_upper)
            ]

        if df.empty:
            continue

        # =========================
        # CONTROLE DE ORIGEM
        # =========================
        df["conta"] = conta.upper()

        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)
