from datetime import date, timedelta
<<<<<<< HEAD
=======
<<<<<<< HEAD

=======
>>>>>>> dev
>>>>>>> origin/dev
from app.analysis.ordens_servico import carregar_ordens_servico_df


def main():
    df = carregar_ordens_servico_df(
        conta="mania",
        data_inicio=date.today() - timedelta(days=7),
        data_fim=date.today(),
        tipo_data="data_cadastro",
<<<<<<< HEAD

        pagina=1,

=======
<<<<<<< HEAD
=======
        pagina=1,
>>>>>>> dev
>>>>>>> origin/dev
        itens_por_pagina=50,
    )

    print("\n=== ORDENS DE SERVIÇO ===")
<<<<<<< HEAD

=======
<<<<<<< HEAD
>>>>>>> origin/dev
    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))

    print(df.head())
    print("\nColunas:")
    print(df.columns.tolist())
    print("\nTotal:", len(df))
<<<<<<< HEAD

    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))

=======
>>>>>>> dev
>>>>>>> origin/dev


if __name__ == "__main__":
    main()
