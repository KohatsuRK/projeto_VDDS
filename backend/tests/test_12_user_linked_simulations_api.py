from uuid import uuid4

from fastapi.testclient import TestClient

from credit_engine.main import app, get_credit_service, get_user_service
from credit_engine.service import CreditService
from credit_engine.user_service import UserService
from credit_engine.repository import InMemoryCreditRepository, InMemoryUserRepository


# Cria um cliente HTTP com serviços isolados para os testes da API.
def criar_client():
    user_repo = InMemoryUserRepository()
    user_service = UserService(user_repo)

    credit_repo = InMemoryCreditRepository()
    credit_service = CreditService(credit_repo)

    app.dependency_overrides[get_user_service] = lambda: user_service
    app.dependency_overrides[get_credit_service] = lambda: credit_service

    client = TestClient(app)
    return client


# Gera dados únicos para evitar interferência entre testes.
def sufixo_unico() -> str:
    return uuid4().hex[:8]


# Verifica se o endpoint de avaliação aceita acesso anônimo.
def test_evaluate_credit_allows_anonymous_user():
    client = criar_client()

    payload = {
        "nome": f"Anonimo {sufixo_unico()}",
        "idade": 30,
        "rendaMensal": 8000.0,
        "scoreCredito": 800,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    response = client.post("/api/v1/credit/evaluate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "status_proposta" in body
    assert "motivo_decisao" in body


# Verifica se o endpoint de avaliação aceita usuário autenticado.
def test_evaluate_credit_with_authenticated_user():
    client = criar_client()
    sufixo = sufixo_unico()

    register_payload = {
        "nome": f"Davi {sufixo}",
        "email": f"davi_{sufixo}@email.com",
        "senha": "123456"
    }

    login_payload = {
        "email": f"davi_{sufixo}@email.com",
        "senha": "123456"
    }

    credit_payload = {
        "nome": f"Cliente Auth {sufixo}",
        "idade": 30,
        "rendaMensal": 9000.0,
        "scoreCredito": 850,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    client.post("/api/v1/users/register", json=register_payload)
    login_response = client.post("/api/v1/users/login", json=login_payload)
    token = login_response.json()["token"]

    response = client.post(
        "/api/v1/credit/evaluate",
        json=credit_payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert "status_proposta" in body
    assert "motivo_decisao" in body


# Verifica se o histórico do usuário exige autenticação.
def test_me_history_requires_authentication():
    client = criar_client()

    response = client.get("/api/v1/users/me/history")

    assert response.status_code == 401


# Verifica se o histórico do usuário retorna apenas as próprias simulações.
def test_me_history_returns_only_logged_user_simulations():
    client = criar_client()

    sufixo_a = sufixo_unico()
    sufixo_b = sufixo_unico()

    register_a = {
        "nome": f"User A {sufixo_a}",
        "email": f"usera_{sufixo_a}@email.com",
        "senha": "123456"
    }
    login_a = {
        "email": f"usera_{sufixo_a}@email.com",
        "senha": "123456"
    }

    register_b = {
        "nome": f"User B {sufixo_b}",
        "email": f"userb_{sufixo_b}@email.com",
        "senha": "123456"
    }
    login_b = {
        "email": f"userb_{sufixo_b}@email.com",
        "senha": "123456"
    }

    client.post("/api/v1/users/register", json=register_a)
    token_a = client.post("/api/v1/users/login", json=login_a).json()["token"]

    client.post("/api/v1/users/register", json=register_b)
    token_b = client.post("/api/v1/users/login", json=login_b).json()["token"]

    payload_a = {
        "nome": f"Simulacao A {sufixo_a}",
        "idade": 30,
        "rendaMensal": 8500.0,
        "scoreCredito": 820,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    payload_b = {
        "nome": f"Simulacao B {sufixo_b}",
        "idade": 32,
        "rendaMensal": 8700.0,
        "scoreCredito": 830,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    client.post(
        "/api/v1/credit/evaluate",
        json=payload_a,
        headers={"Authorization": f"Bearer {token_a}"}
    )

    client.post(
        "/api/v1/credit/evaluate",
        json=payload_b,
        headers={"Authorization": f"Bearer {token_b}"}
    )

    history_a = client.get(
        "/api/v1/users/me/history",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    history_b = client.get(
        "/api/v1/users/me/history",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert history_a.status_code == 200
    assert history_b.status_code == 200

    body_a = history_a.json()
    body_b = history_b.json()

    nomes_a = [item["nome_proponente"] for item in body_a]
    nomes_b = [item["nome_proponente"] for item in body_b]

    assert f"Simulacao A {sufixo_a}" in nomes_a
    assert f"Simulacao B {sufixo_b}" not in nomes_a

    assert f"Simulacao B {sufixo_b}" in nomes_b
    assert f"Simulacao A {sufixo_a}" not in nomes_b


# Verifica se uma simulação anônima não aparece no histórico do usuário autenticado.
def test_anonymous_simulation_does_not_appear_in_user_history():
    client = criar_client()
    sufixo = sufixo_unico()

    register_payload = {
        "nome": f"User {sufixo}",
        "email": f"user_{sufixo}@email.com",
        "senha": "123456"
    }

    login_payload = {
        "email": f"user_{sufixo}@email.com",
        "senha": "123456"
    }

    payload_anonimo = {
        "nome": f"Anonimo {sufixo}",
        "idade": 30,
        "rendaMensal": 8000.0,
        "scoreCredito": 800,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    payload_usuario = {
        "nome": f"Usuario {sufixo}",
        "idade": 31,
        "rendaMensal": 9000.0,
        "scoreCredito": 850,
        "possuiNomeSujo": False,
        "possuiCoGarantidor": False,
        "tipoFinanciamento": "IMOBILIARIO",
    }

    client.post("/api/v1/credit/evaluate", json=payload_anonimo)

    client.post("/api/v1/users/register", json=register_payload)
    token = client.post("/api/v1/users/login", json=login_payload).json()["token"]

    client.post(
        "/api/v1/credit/evaluate",
        json=payload_usuario,
        headers={"Authorization": f"Bearer {token}"}
    )

    history = client.get(
        "/api/v1/users/me/history",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert history.status_code == 200

    nomes = [item["nome_proponente"] for item in history.json()]

    assert f"Usuario {sufixo}" in nomes
    assert f"Anonimo {sufixo}" not in nomes