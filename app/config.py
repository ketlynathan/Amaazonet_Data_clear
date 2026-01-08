import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# ======================================================
# LOAD ENV
# ======================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# ======================================================
# HUBSOFT ACCOUNT CONFIG
# ======================================================
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
    """
    Retorna a configuração HubSoft para a conta informada.
    Contas válidas: mania | amazonet
    """
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


# ======================================================
# GOOGLE SHEETS CONFIG
# ======================================================
@dataclass(frozen=True)
class GoogleSheetsConfig:
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    spreadsheet_id: str
    sheet_name: str


def get_google_sheets_config() -> GoogleSheetsConfig:
    """
    Retorna configuração do Google Sheets (Service Account)
    """
    return GoogleSheetsConfig(
        project_id=_get_env("GOOGLE_PROJECT_ID"),
        private_key_id=_get_env("GOOGLE_PRIVATE_KEY_ID"),
        private_key=_get_env("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        client_email=_get_env("GOOGLE_CLIENT_EMAIL"),
        client_id=_get_env("GOOGLE_CLIENT_ID"),
        spreadsheet_id=_get_env("GOOGLE_SHEET_ID"),
        sheet_name=_get_env("GOOGLE_SHEET_NAME"),
    )
