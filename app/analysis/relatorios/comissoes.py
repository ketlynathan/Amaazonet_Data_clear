from __future__ import annotations

from datetime import date
from typing import List
import pandas as pd


def relatorio_comissoes_df(
    contas: List[str],
    data_inicio: date,
    data_fim: date,
) -> pd.DataFrame:
    """
    🚧 Relatório de Comissões temporariamente desativado

    Motivo:
    - Estrutura de cálculo ainda em validação
    - Evita erro de import no Streamlit
    """
    return pd.DataFrame()
