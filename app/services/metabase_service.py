import os
import json
import urllib.parse
from datetime import date
from typing import Dict, Tuple

import requests
import pandas as pd
from dotenv import load_dotenv

# ======================================================
# LOAD ENV
# ======================================================
load_dotenv()

# ======================================================
# CONFIGURAÇÃO POR CONTA
# ======================================================
CONTAS_CONFIG: Dict[str, Tuple[str | None, str | None]] = {
    "mania": (
        os.getenv("MANIA_BASE_URL"),
        os.getenv("MANIA_CARD_ID"),
    ),
    "amazonet": (
        os.getenv("AMAZONET_BASE_URL"),
        os.getenv("AMAZONET_CARD_ID"),
    ),
}

# ======================================================
# UTIL — MONTA URL METABASE
# ======================================================
def _montar_url(
    base_url: str,
    card_id: str,
    data_inicio: date,
    data_fim: date,
) -> str:
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

    params = urllib.parse.quote(json.dumps(parameters))

    return (
        f"{base_url}/api/public/card/{card_id}/query/json"
        f"?parameters={params}"
    )

# ======================================================
# NORMALIZAÇÃO (ANTI-QUEBRA)
# ======================================================
def _normalizar_df(df: pd.DataFrame, conta: str) -> pd.DataFrame:
    if df.empty:
        return df

    rename_map = {
        "numero": "numero_ordem_servico",
        "tecnico": "usuario_fechamento",
        "usuario_fechamento.name": "usuario_fechamento",
        "tipo_ordem_servico.descricao": "tipo_ordem_servico",
    }

    df = df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}
    )

    # Datas (defensivo)
    for col in ["data_termino_executado", "data_cadastro_os"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    df["conta"] = conta.upper()

    return df

# ======================================================
# SERVICE — FECHAMENTO METABASE
# ======================================================
def carregar_fechamento_metabase(
    conta: str,
    data_inicio: date,
    data_fim: date,
) -> pd.DataFrame:
    """
    Carrega fechamento técnico via Metabase (public card)
    """

    conta = conta.lower().strip()

    config = CONTAS_CONFIG.get(conta)
    if not config:
        raise ValueError(f"Conta inválida: {conta}")

    base_url, card_id = config

    if not base_url or not card_id:
        raise RuntimeError(
            f"Configuração ausente no .env para conta: {conta}"
        )

    url = _montar_url(base_url, card_id, data_inicio, data_fim)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        data = response.json()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        return _normalizar_df(df, conta)

    except requests.RequestException as e:
        print("======================================")
        print(f"[ERRO METABASE - {conta.upper()}]")
        print("URL:", url)
        print("ERRO:", e)
        print("======================================")
        return pd.DataFrame()

    except Exception as e:
        print("======================================")
        print(f"[ERRO INESPERADO METABASE - {conta.upper()}]")
        print("URL:", url)
        print("ERRO:", e)
        print("======================================")
        return pd.DataFrame()
