from fastapi.testclient import TestClient

from credit_engine.main import app

client = TestClient(app)


# Verifica se o endpoint de cadastro cria um novo usuário.
def test_register_user():
    payload = {
        "nome": "Davi Torres",
        "email": "davi@email.com",
        "senha": "123456"
    }

    response = client.post("/api/v1/users/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "Davi Torres"
    assert body["email"] == "davi@email.com"


# Verifica se o endpoint de login retorna um token válido.
def test_login_user():
    register_payload = {
        "nome": "Davi Torres",
        "email": "davi@email.com",
        "senha": "123456"
    }

    login_payload = {
        "email": "davi@email.com",
        "senha": "123456"
    }

    client.post("/api/v1/users/register", json=register_payload)
    response = client.post("/api/v1/users/login", json=login_payload)

    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert body["usuario"]["email"] == "davi@email.com"


# Verifica se o endpoint /me retorna o usuário autenticado.
def test_me_user():
    register_payload = {
        "nome": "Davi Torres",
        "email": "davi@email.com",
        "senha": "123456"
    }

    login_payload = {
        "email": "davi@email.com",
        "senha": "123456"
    }

    client.post("/api/v1/users/register", json=register_payload)
    login_response = client.post("/api/v1/users/login", json=login_payload)

    token = login_response.json()["token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "davi@email.com"