import pytest

from app.hubsoft.factory import get_hubsoft_client


@pytest.mark.integration
def test_hubsoft_mania_authentication():
    client = get_hubsoft_client("mania")

    client.authenticate()

    assert client.token is not None
    assert client.token != ""
    assert "Authorization" in client.session.headers


@pytest.mark.integration
def test_hubsoft_amazonet_authentication():
    client = get_hubsoft_client("amazonet")

    client.authenticate()

    assert client.token is not None
    assert client.token != ""
    assert "Authorization" in client.session.headers
