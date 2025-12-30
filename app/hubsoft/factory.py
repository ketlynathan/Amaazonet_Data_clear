from app.config import get_hubsoft_account_config
from app.hubsoft.client import HubSoftClient


def get_hubsoft_client(account: str) -> HubSoftClient:
    config = get_hubsoft_account_config(account)
    return HubSoftClient(config)
