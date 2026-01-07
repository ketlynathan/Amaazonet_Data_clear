from datetime import date, timedelta
from app.analysis.ordens_servico import carregar_ordens_servico_df


def main():
    df = carregar_ordens_servico_df(
        conta="mania",
        data_inicio=date.today() - timedelta(days=7),
        data_fim=date.today(),
        tipo_data="data_cadastro",

        pagina=1,

        itens_por_pagina=50,
    )

    print("\n=== ORDENS DE SERVIÇO ===")

    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))

    print(df.head())
    print("\nColunas:")
    print(df.columns.tolist())
    print("\nTotal:", len(df))

    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))



if __name__ == "__main__":
    main()
