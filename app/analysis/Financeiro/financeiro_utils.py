import pandas as pd

def padronizar_campos_chave(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip().str.upper()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip().str.upper()
    return df
