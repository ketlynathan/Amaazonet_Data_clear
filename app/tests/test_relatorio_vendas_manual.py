from datetime import date
from app.analysis.relatorios.vendas import relatorio_vendas_df


def main():
    df = relatorio_vendas_df(
        contas=["mania"],
        data_inicio=date(2025, 12, 1),
        data_fim=date(2025, 12, 30),
    )

    print("\n=== RELATÓRIO DE VENDAS ===")
    print(df.head())
    print("\nTotal:", len(df))


if __name__ == "__main__":
    main()
