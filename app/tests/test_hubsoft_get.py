from app.hubsoft.factory import get_hubsoft_client


def test_get_usuarios_mania():
    client = get_hubsoft_client("mania")
    data = client.get("configuracao/geral/usuario")

    assert isinstance(data, dict)
    assert "usuarios" in data


def test_get_usuarios_amazonet():
    client = get_hubsoft_client("amazonet")
    data = client.get("configuracao/geral/usuario")

    assert isinstance(data, dict)
