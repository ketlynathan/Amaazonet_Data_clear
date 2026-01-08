def carregar_status_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.lower().str.strip()
    return df
