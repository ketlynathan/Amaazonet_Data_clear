import pandas as pd
import streamlit as st
from typing import List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.config import get_google_sheets_config

# ======================================================
# GOOGLE API
# ======================================================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


@st.cache_resource(show_spinner=False)
def get_sheets_service():
    """
    Cria e cacheia o client da Google Sheets API
    """
    cfg = get_google_sheets_config()

    credentials = Credentials.from_service_account_info(
    {
        "type": "service_account",
        "project_id": cfg.project_id,
        "private_key_id": cfg.private_key_id,
        "private_key": cfg.private_key.replace("\\n", "\n"),
        "client_email": cfg.client_email,
        "client_id": cfg.client_id,
        "token_uri": "https://oauth2.googleapis.com/token",
    },
    scopes=SCOPES,
)

    return build("sheets", "v4", credentials=credentials)


# ======================================================
# LEITURA DA PLANILHA
# ======================================================
@st.cache_data(ttl=300, show_spinner=False)
def read_sheet_as_dataframe() -> pd.DataFrame:
    """
    Lê a aba configurada do Google Sheets e retorna DataFrame
    """
    cfg = get_google_sheets_config()
    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=cfg.spreadsheet_id,
            range=cfg.sheet_name,
        )
        .execute()
    )

    values = result.get("values", [])

    if not values or len(values) < 2:
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


# ======================================================
# NORMALIZAÇÃO DE CABEÇALHOS
# ======================================================
def normalize_headers(headers: List[str]) -> List[str]:
    """
    Garante colunas:
    - sem vazios
    - sem duplicatas
    - limpas
    """
    seen = {}
    normalized = []

    for i, col in enumerate(headers):
        col = (col or "").strip().replace("\n", " ")

        if not col:
            col = f"COL_{i+1}"

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 1

        normalized.append(col)

    return normalized
