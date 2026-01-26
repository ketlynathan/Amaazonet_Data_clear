import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=True)


# === HUBSOFT ACCOUNT CONFIG =======================================
@dataclass(frozen=True)
class HubSoftAccountConfig:
    name: str
    token_url: str
    api_base: str
    client_id: str
    client_secret: str
    user: str
    password: str
    timeout: int = 30


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Variável de ambiente ausente: {name}")
    return value


def get_hubsoft_account_config(account: str) -> HubSoftAccountConfig:
    account = account.upper()

    if account not in {"MANIA", "AMAZONET"}:
        raise ValueError("Conta HubSoft inválida. Use 'mania' ou 'amazonet'.")

    prefix = f"HUBSOFT_{account}_"

    return HubSoftAccountConfig(
        name=account.lower(),
        token_url=_get_env(f"{prefix}TOKEN_URL"),
        api_base=_get_env(f"{prefix}API_BASE"),
        client_id=_get_env(f"{prefix}CLIENT_ID"),
        client_secret=_get_env(f"{prefix}CLIENT_SECRET"),
        user=_get_env(f"{prefix}USER"),
        password=_get_env(f"{prefix}PASSWORD"),
    )


# === GOOGLE SHEETS CONFIG =======================================
@dataclass
class GoogleSheetsConfig:
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str

    # IDs das planilhas
    spreadsheet_60: str
    spreadsheet_51: str
    spreadsheet_51_stm: str
    spreadsheet_39: str

    # Nomes das abas
    sheet_name_60: str
    sheet_name_60_venda: str
    sheet_name_51: str
    sheet_name_51_stm: str
    sheet_name_39: str


def get_google_sheets_config() -> GoogleSheetsConfig:
    return GoogleSheetsConfig(
        project_id=os.getenv("GOOGLE_PROJECT_ID"),
        private_key_id=os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        private_key=os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        client_email=os.getenv("GOOGLE_CLIENT_EMAIL"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),

        # IDs das planilhas
        spreadsheet_60=os.getenv("GOOGLE_SHEET_ID_60"),
        spreadsheet_51=os.getenv("GOOGLE_SHEET_ID_51"),
        spreadsheet_51_stm=os.getenv("GOOGLE_SHEET_ID_51_STM"),
        spreadsheet_39=os.getenv("GOOGLE_SHEET_ID_39"),

        # Nomes das abas
        sheet_name_60=os.getenv("GOOGLE_SHEET_NAME_60"),
        sheet_name_60_venda=os.getenv("GOOGLE_SHEET_NAME_60_VENDA"),
        sheet_name_51=os.getenv("GOOGLE_SHEET_NAME_51"),
        sheet_name_51_stm=os.getenv("GOOGLE_SHEET_NAME_51_STM"),
        sheet_name_39=os.getenv("GOOGLE_SHEET_NAME_39"),
    )



# === METABASE CONFIG =======================================
@dataclass(frozen=True)
class MetabaseReportConfig:
    base_url: str
    cards: dict


def get_metabase_config(account: str) -> MetabaseReportConfig:
    account = account.upper()

    if account not in {"MANIA", "AMAZONET"}:
        raise ValueError("Conta Metabase inválida. Use 'mania' ou 'amazonet'.")

    base_url = _get_env(f"{account}_BASE_URL")

    cards = {
        "fechamento": _get_env(f"{account}_CARD_FECHAMENTO"),
        "qualidade": _get_env(f"{account}_CARD_QUALIDADE"),
        "fila": _get_env(f"{account}_CARD_FILA"),
    }

    return MetabaseReportConfig(
        base_url=base_url,
        cards=cards,
    )
