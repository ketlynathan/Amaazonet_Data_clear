import logging
import pandas as pd
from app.hubsoft.factory import get_hubsoft_client


# ======================================================
# SERVICE
# ======================================================
def carregar_usuarios_df(conta: str) -> pd.DataFrame:
    client = get_hubsoft_client(conta)
    data = client.get("configuracao/geral/usuario")

    usuarios = _extrair_lista_usuarios(data)
    if not usuarios:
        return pd.DataFrame()

    df = pd.json_normalize(usuarios)

    _padronizar_colunas(df)
    df["conta"] = conta.upper()

    return df


# ======================================================
# UTIL
# ======================================================
def _extrair_lista_usuarios(data) -> list:
    if not isinstance(data, dict):
        return []

    return (
        data.get("usuarios")
        or data.get("data")
        or data.get("items")
        or []
    )


def _padronizar_colunas(df: pd.DataFrame) -> None:
    if "name" not in df.columns:
        df["name"] = None


# ======================================================
# DEBUG LOCAL
# ======================================================
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
