import pytest

from credit_engine.user_service import UserService
from credit_engine.repository import InMemoryUserRepository


# Verifica se um usuario pode ser registrado corretamente e se a senha nao fica salva em texto puro.
def test_registrar_usuario():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    usuario = service.registrar_usuario(
        nome="Davi Torres",
        email="davi@email.com",
        senha="123456"
    )

    assert usuario.id == 1
    assert usuario.nome == "Davi Torres"
    assert usuario.email == "davi@email.com"

    salvo = repo.buscar_usuario_por_email("davi@email.com")
    assert salvo is not None
    assert salvo.senha_hash != "123456"
    assert salvo.senha_salt is not None
    assert len(salvo.senha_hash) > 0


# Verifica se o sistema impede cadastro com email ja existente.
def test_email_duplicado():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.registrar_usuario(
        nome="Davi Torres",
        email="davi@email.com",
        senha="123456"
    )

    with pytest.raises(ValueError, match="email ja cadastrado"):
        service.registrar_usuario(
            nome="Outro Nome",
            email="davi@email.com",
            senha="abcdef"
        )


# Verifica se um usuario valido consegue fazer login e receber um token de autenticacao.
def test_login_valido():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.registrar_usuario(
        nome="Davi Torres",
        email="davi@email.com",
        senha="123456"
    )

    resposta = service.login(
        email="davi@email.com",
        senha="123456"
    )

    assert resposta["token"] is not None
    assert len(resposta["token"]) > 10
    assert resposta["usuario"].email == "davi@email.com"


# Verifica se o login falha quando a senha esta incorreta.
def test_login_invalido():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.registrar_usuario(
        nome="Davi Torres",
        email="davi@email.com",
        senha="123456"
    )

    with pytest.raises(ValueError, match="credenciais invalidas"):
        service.login(
            email="davi@email.com",
            senha="senha_errada"
        )


# Verifica se o sistema consegue recuperar o usuario a partir do token gerado no login.
def test_buscar_usuario_por_token():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.registrar_usuario(
        nome="Davi Torres",
        email="davi@email.com",
        senha="123456"
    )

    resposta = service.login(
        email="davi@email.com",
        senha="123456"
    )

    usuario = service.buscar_usuario_por_token(resposta["token"])

    assert usuario is not None
    assert usuario.email == "davi@email.com"