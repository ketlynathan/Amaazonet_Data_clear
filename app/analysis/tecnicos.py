from datetime import date
from app.analysis.ordens_servico import carregar_ordens_servico_df


def carregar_tecnicos_fechamento(
    conta: str,
    data_inicio: date,
    data_fim: date,
) -> list[str]:

    df = carregar_ordens_servico_df(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_data="data_termino_executado",
    )

    if df.empty or "usuario_fechamento.name" not in df.columns:
        return []

    tecnicos = (
        df["usuario_fechamento.name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tecnicos.sort()
    return tecnicos
