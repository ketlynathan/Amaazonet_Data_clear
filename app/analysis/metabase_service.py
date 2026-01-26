import json
import urllib.parse
import requests
import pandas as pd

from app.config import get_metabase_config


# ======================================================
# UTIL
# ======================================================
def _montar_url(base_url: str, card_id: str, data_inicio, data_fim) -> str:
    parameters = [
        {
            "type": "date/single",
            "value": data_inicio.isoformat(),
            "target": ["variable", ["template-tag", "datainicio"]],
        },
        {
            "type": "date/single",
            "value": data_fim.isoformat(),
            "target": ["variable", ["template-tag", "datafim"]],
        },
    ]

    params_str = urllib.parse.quote(json.dumps(parameters))

    return f"{base_url}/api/public/card/{card_id}/query/json?parameters={params_str}"


# ======================================================
# SERVICE GENÉRICO DE RELATÓRIOS METABASE
# ======================================================
def carregar_relatorio_metabase(
    conta: str,
    tipo_relatorio: str,
    data_inicio,
    data_fim,
) -> pd.DataFrame:
    """
    conta: 'mania' ou 'amazonet'
    tipo_relatorio: 'fechamento', 'qualidade', 'fila', etc
    """

    tipo_relatorio = tipo_relatorio.lower()
    config = get_metabase_config(conta)

    card_id = config.cards.get(tipo_relatorio)
    if not card_id:
        raise ValueError(
            f"Relatório '{tipo_relatorio}' não configurado para a conta {conta.upper()}"
        )

    url = _montar_url(config.base_url, card_id, data_inicio, data_fim)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["conta"] = conta.upper()
        df["tipo_relatorio"] = tipo_relatorio.upper()

        return df

    except Exception as e:
        print("======================================")
        print(f"[ERRO METABASE - {conta.upper()} - {tipo_relatorio.upper()}]")
        print("URL:", url)
        print("ERRO:", e)
        print("======================================")
        return pd.DataFrame()


# ======================================================
# FUNÇÕES ESPECÍFICAS (OPCIONAL – AÇÚCAR SINTÁTICO)
# ======================================================
def carregar_fechamento_metabase(conta: str, data_inicio, data_fim) -> pd.DataFrame:
    return carregar_relatorio_metabase(conta, "fechamento", data_inicio, data_fim)


def carregar_qualidade_metabase(conta: str, data_inicio, data_fim) -> pd.DataFrame:
    return carregar_relatorio_metabase(conta, "qualidade", data_inicio, data_fim)


def carregar_fila_metabase(conta: str, data_inicio, data_fim) -> pd.DataFrame:
    return carregar_relatorio_metabase(conta, "fila", data_inicio, data_fim)
