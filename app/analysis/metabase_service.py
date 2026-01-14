import os
import json
import urllib.parse
import requests
import pandas as pd
from dotenv import load_dotenv

# ======================================================
# LOAD ENV
# ======================================================
load_dotenv()

MANIA_BASE_URL = os.getenv("MANIA_BASE_URL")
AMAZONET_BASE_URL = os.getenv("AMAZONET_BASE_URL")

MANIA_CARD_ID = os.getenv("MANIA_CARD_ID")
AMAZONET_CARD_ID = os.getenv("AMAZONET_CARD_ID")


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

    return (
        f"{base_url}/api/public/card/{card_id}/query/json"
        f"?parameters={params_str}"
    )


# ======================================================
# SERVICE
# ======================================================
def carregar_fechamento_metabase(
    conta: str,
    data_inicio,
    data_fim,
) -> pd.DataFrame:

    if conta == "mania":
        base_url = MANIA_BASE_URL
        card_id = MANIA_CARD_ID

    elif conta == "amazonet":
        base_url = AMAZONET_BASE_URL
        card_id = AMAZONET_CARD_ID

    else:
        return pd.DataFrame()

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
        df["conta"] = conta.upper()

        return df

    except Exception as e:
        print("======================================")
        print(f"[ERRO METABASE - {conta.upper()}]")
        print("URL:", url)
        print("ERRO:", e)
        print("======================================")
        return pd.DataFrame()
