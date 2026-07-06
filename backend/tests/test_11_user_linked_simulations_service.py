from credit_engine.schemas import ClienteSchema
from credit_engine.service import CreditService
from credit_engine.repository import InMemoryCreditRepository


# Cria um cliente válido para os testes de serviço.
def criar_cliente(nome: str) -> ClienteSchema:
    return ClienteSchema(
        nome=nome,
        idade=30,
        renda_mensal=8000.0,
        score_credito=800,
        possui_nome_sujo=False,
        possui_co_garantidor=False,
        tipo_financiamento="IMOBILIARIO",
    )


# Verifica se uma simulação anônima é salva sem usuario_id.
def test_simulacao_anonima_salva_sem_usuario():
    repo = InMemoryCreditRepository()
    service = CreditService(repo)

    cliente = criar_cliente("Cliente Anonimo")
    service.avaliar_credito(cliente)

    registro = repo.listar_simulacoes(limite=1)[0]

    assert registro.nome_proponente == "Cliente Anonimo"
    assert registro.usuario_id is None


# Verifica se uma simulação autenticada é salva com usuario_id.
def test_simulacao_autenticada_salva_com_usuario():
    repo = InMemoryCreditRepository()
    service = CreditService(repo)

    cliente = criar_cliente("Cliente Autenticado")
    service.avaliar_credito(cliente, usuario_id=7)

    registro = repo.listar_simulacoes(limite=1)[0]

    assert registro.nome_proponente == "Cliente Autenticado"
    assert registro.usuario_id == 7


# Verifica se o hash muda entre contexto anônimo e autenticado.
def test_hash_muda_entre_anonimo_e_autenticado():
    repo = InMemoryCreditRepository()
    service = CreditService(repo)

    cliente = criar_cliente("Cliente Hash")

    hash_anonimo = service._gerar_hash(cliente)
    hash_usuario = service._gerar_hash(cliente, usuario_id=5)

    assert hash_anonimo != hash_usuario


# Verifica se o histórico pode ser filtrado por usuário.
def test_historico_filtrado_por_usuario():
    repo = InMemoryCreditRepository()
    service = CreditService(repo)

    cliente_a = criar_cliente("Cliente Usuario 1")
    cliente_b = criar_cliente("Cliente Usuario 2")
    cliente_c = criar_cliente("Cliente Anonimo 2")

    service.avaliar_credito(cliente_a, usuario_id=1)
    service.avaliar_credito(cliente_b, usuario_id=2)
    service.avaliar_credito(cliente_c)

    historico_usuario_1 = service.listar_historico(usuario_id=1)
    historico_usuario_2 = service.listar_historico(usuario_id=2)
    historico_geral = service.listar_historico()

    assert len(historico_usuario_1) == 1
    assert historico_usuario_1[0].nome_proponente == "Cliente Usuario 1"
    assert historico_usuario_1[0].usuario_id == 1

    assert len(historico_usuario_2) == 1
    assert historico_usuario_2[0].nome_proponente == "Cliente Usuario 2"
    assert historico_usuario_2[0].usuario_id == 2

    assert len(historico_geral) == 3


# Verifica se duas simulações iguais podem coexistir quando uma é anônima e outra autenticada.
def test_simulacao_anonima_e_autenticada_nao_colidem_no_cache():
    repo = InMemoryCreditRepository()
    service = CreditService(repo)

    cliente = criar_cliente("Cliente Escopo")

    resposta_anonima = service.avaliar_credito(cliente)
    resposta_autenticada = service.avaliar_credito(cliente, usuario_id=10)

    historico = service.listar_historico()

    assert len(historico) == 2
    assert resposta_anonima.status_proposta == resposta_autenticada.status_proposta