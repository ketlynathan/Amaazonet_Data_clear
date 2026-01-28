import pandas as pd
import streamlit as st
import time
from typing import List
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
# Leitor resiliente das planilhas
# ============================================================
@st.cache_data(ttl=300)
def read_sheet_as_dataframe(sheet_key: str = "60", start_row: int = 1):
    cfg = get_google_sheets_config()
    service = get_sheets_service()

    # 🔁 Mapeamento completo restaurado
    sheet_map = {
        "60": (cfg.spreadsheet_60, cfg.sheet_name_60),
        "60_venda": (cfg.spreadsheet_60, cfg.sheet_name_60_venda),
        "51": (cfg.spreadsheet_51, cfg.sheet_name_51),
        "51_STM": (cfg.spreadsheet_51_stm, cfg.sheet_name_51_stm),
        "39": (cfg.spreadsheet_39, cfg.sheet_name_39),
    }

    if sheet_key not in sheet_map:
        raise ValueError(f"Planilha inválida: {sheet_key}")

    spreadsheet_id, sheet_name = sheet_map[sheet_key]
    sheet_name = sheet_name.strip()

    range_str = f"'{sheet_name}'!A{start_row}:ZZ"
    tentativas = 3

    for tentativa in range(tentativas):
        try:
            result = (
                service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_str
                )
                .execute()
            )
            break
        except HttpError as e:
            if e.resp.status in [429, 500, 503]:
                if tentativa < tentativas - 1:
                    time.sleep(2 + tentativa)
                    continue
                raise RuntimeError(
                    "⚠️ Google Sheets temporariamente indisponível. Tente novamente."
                )
            raise e

    values = result.get("values", [])

    if not values:
        return pd.DataFrame()

    headers = normalize_headers(values[0])
    rows = values[1:]
    num_cols = len(headers)

    normalized_rows = [
        row[:num_cols] + [""] * (num_cols - len(row))
        for row in rows
    ]

    return pd.DataFrame(normalized_rows, columns=headers)


# ============================================================
# Normalizador de cabeçalhos
# ============================================================
def normalize_headers(headers: List[str]) -> List[str]:
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
