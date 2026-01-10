import pandas as pd
import streamlit as st
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import get_google_sheets_config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


# ============================================================
# Google Sheets Service (1 vez por sessão)
# ============================================================
@st.cache_resource
def get_sheets_service():
    cfg = get_google_sheets_config()

    credentials = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": cfg.project_id,
            "private_key_id": cfg.private_key_id,
            "private_key": cfg.private_key,
            "client_email": cfg.client_email,
            "client_id": cfg.client_id,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPES,
    )

    return build("sheets", "v4", credentials=credentials)


# ============================================================
# Leitor resiliente das planilhas 51 e 60
# ============================================================
@st.cache_data(ttl=300)
def read_sheet_as_dataframe(sheet_key="60"):
    cfg = get_google_sheets_config()
    service = get_sheets_service()

    # Mapeia qual planilha usar
    sheet_map = {
        "51": cfg.spreadsheet_51,
        "60": cfg.spreadsheet_60,
    }

    spreadsheet_id = sheet_map.get(sheet_key)

    if not spreadsheet_id:
        raise ValueError(f"Planilha inválida: {sheet_key}")

    tentativas = 3

    for tentativa in range(tentativas):
        try:
            result = (
                service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=f"'{cfg.sheet_name}'"
                )
                .execute()
            )
            break
        except HttpError as e:
            # Proteção contra Google instável
            if e.resp.status in [429, 500, 503]:
                if tentativa < tentativas - 1:
                    time.sleep(2 + tentativa)
                    continue
                else:
                    raise RuntimeError(
                        "⚠️ Google Sheets temporariamente indisponível. Tente novamente em alguns segundos."
                    )
            else:
                raise e

    values = result.get("values", [])

    if len(values) < 2:
        return pd.DataFrame()

    raw_headers = values[0]
    rows = values[1:]

    headers = normalize_headers(raw_headers)
    num_cols = len(headers)

    normalized_rows = [
        row[:num_cols] + [""] * (num_cols - len(row))
        for row in rows
    ]

    return pd.DataFrame(normalized_rows, columns=headers)


# ============================================================
# Normalizador de cabeçalhos
# ============================================================
def normalize_headers(headers: list[str]) -> list[str]:
    seen = {}
    normalized = []

    for i, col in enumerate(headers):
        col = (col or "").strip()

        if not col:
            col = f"COL_{i+1}"

        col = col.replace("\n", " ").strip()

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 1

        normalized.append(col)

    return normalized
