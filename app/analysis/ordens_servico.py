import pandas as pd
from datetime import date
from typing import Optional

from app.hubsoft.factory import get_hubsoft_client


def carregar_ordens_servico_df(
    conta: str,
    data_inicio: date,
    data_fim: date,
    tipo_data: str = "data_cadastro",
    itens_por_pagina: int = 100,
    max_paginas: int = 50,  # limite de segurança
    tecnico: Optional[str] = None,
    tipo_ordem_servico: Optional[str] = None,
) -> pd.DataFrame:
    """
    Carrega ordens de serviço da API HubSoft com paginação e filtros opcionais.
    Retorna DataFrame normalizado e pronto para uso na UI.
    """

    client = get_hubsoft_client(conta)

    pagina = 1
    todas_ordens: list[dict] = []

    # ======================================================
    # PAGINAÇÃO
    # ======================================================
    while pagina <= max_paginas:
        payload = {
            "pagina": pagina,
            "itens_por_pagina": itens_por_pagina,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
            "tipo_data": tipo_data,
        }

        # -------------------------
        # FILTROS OPCIONAIS
        # -------------------------

        if tecnico:
            payload["usuario_fechamento.nome"] = tecnico

        if tipo_ordem_servico:
            payload["tipo_ordem_servico.descricao"] = tipo_ordem_servico

        response = client.get(
            "integracao/ordem_servico/todos",
            params=payload,
        )

        if not isinstance(response, dict):
            break

        ordens = (
            response.get("ordens_servico")
            or response.get("ordens")
            or response.get("data")
            or []
        )

        if not isinstance(ordens, list) or not ordens:
            break

        todas_ordens.extend(ordens)
        pagina += 1

    # ======================================================
    # SEM DADOS
    # ======================================================
    if not todas_ordens:
        return pd.DataFrame()

    # ======================================================
    # NORMALIZAÇÃO FINAL
    # ======================================================
    df = pd.json_normalize(todas_ordens)

    # -------------------------
    # PADRONIZAÇÃO DE COLUNAS
    # -------------------------
    MAPA_COLUNAS = {
        "usuario_fechamento.nome": "tecnico",
        "usuario_abertura": "usuario_abertura",
    }

    for origem, destino in MAPA_COLUNAS.items():
        if origem in df.columns:
            df[destino] = df[origem]

    # -------------------------
    # DATAS
    # -------------------------
    if "data_cadastro" in df.columns:
        df["data_cadastro"] = pd.to_datetime(
            df["data_cadastro"], errors="coerce"
        )

    if "data_fechamento" in df.columns:
        df["data_fechamento"] = pd.to_datetime(
            df["data_fechamento"], errors="coerce"
        )

    df["conta"] = conta.upper()

    return df
