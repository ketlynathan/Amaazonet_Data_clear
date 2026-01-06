import time
import traceback

from app.hubsoft.factory import get_hubsoft_client


ENDPOINTS_TESTE = [
    "configuracao/geral/usuario",
    "configuracao/usuario",
    "usuario",
]


def testar_conta(conta: str):
    print(f"\n🔍 Testando conta: {conta.upper()}")
    print("-" * 50)

    try:
        client = get_hubsoft_client(conta)

        inicio = time.time()
        client.authenticate()
        tempo_auth = time.time() - inicio

        print(f"🟢 Autenticação OK ({tempo_auth:.2f}s)")

        for endpoint in ENDPOINTS_TESTE:
            try:
                inicio = time.time()
                response = client.get(endpoint)
                tempo = time.time() - inicio

                total = (
                    len(response)
                    if isinstance(response, list)
                    else len(response.get("data", []))
                    if isinstance(response, dict)
                    else "?"
                )

                print(f"🟢 {endpoint} → OK ({tempo:.2f}s) | registros: {total}")

            except Exception as e:
                print(f"🔴 {endpoint} → ERRO")
                print(f"   {type(e).__name__}: {e}")

    except Exception as e:
        print("🔴 ERRO GERAL NA CONTA")
        traceback.print_exc()


def main():
    for conta in ["mania", "amazonet"]:
        testar_conta(conta)


if __name__ == "__main__":
    main()
