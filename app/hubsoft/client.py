import logging
import requests
from app.config import HubSoftAccountConfig

logger = logging.getLogger(__name__)


class HubSoftClient:
    def __init__(self, config: HubSoftAccountConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.token: str | None = None

        logger.info(
            "Inicializando HubSoftClient",
            extra={
                "conta": self.config.name,
                "api_base": self.config.api_base,
            },
        )

    def authenticate(self) -> None:
        logger.info(
            "Iniciando autenticação HubSoft",
            extra={
                "conta": self.config.name,
                "token_url": self.config.token_url,
            },
        )

        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "username": self.config.user,
            "password": self.config.password,
            "grant_type": "password",
        }

        logger.debug(
            "Payload de autenticação preparado",
            extra={"conta": self.config.name},
        )

        response = self.session.post(
            self.config.token_url,
            json=payload,
            timeout=self.config.timeout,
        )

        logger.info(
            "Resposta recebida",
            extra={
                "conta": self.config.name,
                "status": response.status_code,
            },
        )

        response.raise_for_status()

        token = response.json().get("access_token")
        if not token:
            raise RuntimeError(
                f"Token não retornado pela API HubSoft ({self.config.name})"
            )

        self.token = token
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            }
        )

        logger.info(
            "Autenticação concluída com sucesso",
            extra={"conta": self.config.name},
        )

    def _ensure_authenticated(self) -> None:
        if not self.token:
            self.authenticate()

    def get(self, path: str, params: dict | None = None) -> dict:
        """
        GET genérico para a API HubSoft
        """
        self._ensure_authenticated()

        url = f"{self.config.api_base}/{path.lstrip('/')}"
        logger.info(
            "Executando GET HubSoft",
            extra={
                "conta": self.config.name,
                "url": url,
                "params": params,
            },
        )

        response = self.session.get(
            url,
            params=params,
            timeout=self.config.timeout,
        )

        logger.info(
            "Resposta GET recebida",
            extra={
                "conta": self.config.name,
                "status": response.status_code,
            },
        )

        response.raise_for_status()
        return response.json()
