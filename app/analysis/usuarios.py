
import logging
import pandas as pd
from app.hubsoft.factory import get_hubsoft_client


def carregar_usuarios_df(conta: str) -> pd.DataFrame:
    client = get_hubsoft_client(conta)

    data = client.get("configuracao/geral/usuario")

    # defensivo
    if not isinstance(data, dict):
        return pd.DataFrame()

    usuarios = (
        data.get("usuarios")
        or data.get("data")
        or data.get("items")
        or []
    )

    if not isinstance(usuarios, list):
        return pd.DataFrame()

    df = pd.json_normalize(usuarios)

    # padroniza colunas importantes
    if "name" not in df.columns:
        df["name"] = None

    df["conta"] = conta.upper()

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

