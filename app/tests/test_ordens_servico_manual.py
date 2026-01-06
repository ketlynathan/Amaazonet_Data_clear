from datetime import date, timedelta
<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> dev
=======

>>>>>>> feature/relatorio-fechamento-tecnico
from app.analysis.ordens_servico import carregar_ordens_servico_df


def main():
    df = carregar_ordens_servico_df(
        conta="mania",
        data_inicio=date.today() - timedelta(days=7),
        data_fim=date.today(),
        tipo_data="data_cadastro",
<<<<<<< HEAD
<<<<<<< HEAD
=======
        pagina=1,
>>>>>>> dev
=======
>>>>>>> feature/relatorio-fechamento-tecnico
        itens_por_pagina=50,
    )

    print("\n=== ORDENS DE SERVIÇO ===")
<<<<<<< HEAD
<<<<<<< HEAD
    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))
=======
    print(df.head())
    print("\nColunas:")
    print(df.columns.tolist())
    print("\nTotal:", len(df))
>>>>>>> dev
=======
    print(df.head(10))

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== TOTAL DE REGISTROS ===")
    print(len(df))
>>>>>>> feature/relatorio-fechamento-tecnico


if __name__ == "__main__":
    main()
