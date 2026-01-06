from __future__ import annotations

from datetime import date
from functools import lru_cache
from typing import List

import pandas as pd

from app.analysis.ordens_servico import carregar_ordens_servico_df


# ============================================================
# CONFIGURAÇÕES DE NEGÓCIO
# ============================================================

TIPOS_VENDA: tuple[str, ...] = (
    "INSTALAÇÃO",
    "VENDA",
    "MIGRAÇÃO",
    "UPGRADE",
    "ADESÃO",
)

TIPO_DATA_VENDA = "data_cadastro"


# ============================================================
# FUNÇÕES INTERNAS (CACHEADAS)
# ============================================================

@lru_cache(maxsize=32)
def _carregar_vendas_conta(
    conta: str,
    data_inicio: date,
    data_fim: date,
) -> pd.DataFrame:
    """
    Carrega ordens de serviço de uma conta e filtra apenas vendas.
    Cacheado por conta + período.
    """

    df = carregar_ordens_servico_df(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data=TIPO_DATA_VENDA,
    )

    if df.empty:
        return df

    # 🔍 Filtro por tipos de venda
    padrao_venda = "|".join(TIPOS_VENDA)
    df = df[df["tipo"].str.contains(padrao_venda, case=False, na=False)]

    df["conta"] = conta.upper()

    return df


# ============================================================
# FUNÇÃO PÚBLICA
# ============================================================

def relatorio_vendas_df(
    contas: List[str],
    data_inicio: date,
    data_fim: date,
) -> pd.DataFrame:
    """
    Relatório consolidado de vendas (todas as contas).
    """

    dfs: list[pd.DataFrame] = []

    for conta in contas:
        df = _carregar_vendas_conta(
            conta=conta,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        if not df.empty:
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs, ignore_index=True)

    # ========================================================
    # ORGANIZAÇÃO DE COLUNAS
    # ========================================================

    colunas_prioritarias = [
        "id_ordem_servico",
        "numero",
        "tipo",
        "status",
        "conta",
        "data_cadastro",
        "usuario_fechamento",
        "dados_cliente.nome",
        "dados_endereco_instalacao.cidade",
        "dados_endereco_instalacao.estado",
    ]

    colunas_existentes = [c for c in colunas_prioritarias if c in df_final.columns]
    colunas_restantes = [c for c in df_final.columns if c not in colunas_existentes]

    return df_final[colunas_existentes + colunas_restantes]
