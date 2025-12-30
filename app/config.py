import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


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
