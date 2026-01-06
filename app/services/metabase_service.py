import requests
import os
import pandas as pd
import json
import urllib.parse
from datetime import date
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
# URL BUILDER
# ======================================================
def _montar_url(base_url: str, card_id: str, data_inicio: date, data_fim: date) -> str:
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

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Datas
    for col in ["data_termino_executado", "data_cadastro_os"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    df["conta"] = conta.upper()

    return df


# ======================================================
# LOAD PRINCIPAL
# ======================================================
def carregar_fechamento_metabase(
    conta: str,
    data_inicio: date,
    data_fim: date,
) -> pd.DataFrame:

    if conta == "mania":
        base_url = MANIA_BASE_URL
        card_id = MANIA_CARD_ID

    elif conta == "amazonet":
        base_url = AMAZONET_BASE_URL
        card_id = AMAZONET_CARD_ID

    else:
        return pd.DataFrame()

    url = _montar_url(base_url, card_id, data_inicio, data_fim)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        data = response.json()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = _normalizar_df(df, conta)

        return df

    except Exception as e:
        print(f"[ERRO METABASE - {conta.upper()}]")
        print(url)
        print(e)
        return pd.DataFrame()
