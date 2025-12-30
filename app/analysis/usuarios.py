import logging
import pandas as pd

from app.hubsoft.factory import get_hubsoft_client


logger = logging.getLogger(__name__)


def carregar_usuarios_df(conta: str) -> pd.DataFrame:
    logger.info("Carregando usuários | conta=%s", conta)

    client = get_hubsoft_client(conta)

    # Chamada API
    response = client.get("configuracao/geral/usuario")

    usuarios = response.get("usuarios")

    if not isinstance(usuarios, list):
        raise ValueError(
            f"Estrutura inesperada de usuários | tipo={type(usuarios)}"
        )

    df = pd.json_normalize(usuarios)

    logger.info(
        "Usuários carregados com sucesso | conta=%s | linhas=%d | colunas=%d",
        conta,
        df.shape[0],
        df.shape[1],
    )

    return df


def _debug():
    df = carregar_usuarios_df("mania")

    print("\n=== HEAD USUÁRIOS (MANIA) ===")
    print(df.head())

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    _debug()
