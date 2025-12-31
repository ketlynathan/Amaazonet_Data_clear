from datetime import date, timedelta

from app.analysis.tecnicos import carregar_tecnicos


def main():
    conta = "mania"
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=7)

    tecnicos = carregar_tecnicos(
        conta=conta,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    print("\n=== TÉCNICOS ENCONTRADOS ===")

    if not tecnicos:
        print("⚠️ Nenhum técnico encontrado")
        return

    for t in tecnicos:
        print("-", t)

    print("\nTotal de técnicos:", len(tecnicos))


if __name__ == "__main__":
    main()
