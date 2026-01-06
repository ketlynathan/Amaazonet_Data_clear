from app.hubsoft.factory import get_hubsoft_client

def main():
    client = get_hubsoft_client("mania")

    usuarios = client.get("configuracao/geral/usuario")

    print("Resposta:")
    print(usuarios)

if __name__ == "__main__":
    main()
