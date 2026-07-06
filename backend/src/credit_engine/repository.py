
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timezone


# Representa uma simulação de crédito desacoplada do ORM.
class SimulacaoRecord:

    # Inicializa os dados de uma simulação persistida.
    def __init__(
        self,
        id: int,
        nome_proponente: str,
        status_proposta: str,
        taxa_juros_aplicada: Optional[float],
        motivo_decisao: str,
        data_processamento: datetime,
        hash_requisicao: str,
        usuario_id: Optional[int] = None,
    ):
        self.id = id
        self.nome_proponente = nome_proponente
        self.status_proposta = status_proposta
        self.taxa_juros_aplicada = taxa_juros_aplicada
        self.motivo_decisao = motivo_decisao
        self.data_processamento = data_processamento
        self.hash_requisicao = hash_requisicao
        self.usuario_id = usuario_id


# Define o contrato base do repositório de simulações.
class CreditRepository(ABC):

    # Salva uma simulação e retorna o registro criado.
    @abstractmethod
    def salvar_simulacao(
        self,
        nome_proponente: str,
        status_proposta: str,
        taxa_juros_aplicada: Optional[float],
        motivo_decisao: str,
        hash_requisicao: str,
        usuario_id: Optional[int] = None,
    ) -> SimulacaoRecord:
        ...

    # Busca uma simulação anterior pelo hash da requisição.
    @abstractmethod
    def buscar_por_hash(self, hash_requisicao: str) -> Optional[SimulacaoRecord]:
        ...

    # Lista as simulações mais recentes sem filtro por usuário.
    @abstractmethod
    def listar_simulacoes(self, limite: int = 50) -> list[SimulacaoRecord]:
        ...

    # Lista as simulações mais recentes de um usuário específico.
    @abstractmethod
    def listar_simulacoes_por_usuario(self, usuario_id: int, limite: int = 50) -> list[SimulacaoRecord]:
        ...


# Implementa o repositório de simulações em memória.
class InMemoryCreditRepository(CreditRepository):

    # Inicializa o armazenamento temporário em memória.
    def __init__(self):
        self._storage: list[SimulacaoRecord] = []
        self._next_id: int = 1

    # Salva uma simulação em memória com usuário opcional.
    def salvar_simulacao(
        self,
        nome_proponente: str,
        status_proposta: str,
        taxa_juros_aplicada: Optional[float],
        motivo_decisao: str,
        hash_requisicao: str,
        usuario_id: Optional[int] = None,
    ) -> SimulacaoRecord:
        registro = SimulacaoRecord(
            id=self._next_id,
            nome_proponente=nome_proponente,
            status_proposta=status_proposta,
            taxa_juros_aplicada=taxa_juros_aplicada,
            motivo_decisao=motivo_decisao,
            data_processamento=datetime.now(timezone.utc),
            hash_requisicao=hash_requisicao,
            usuario_id=usuario_id,
        )
        self._storage.append(registro)
        self._next_id += 1
        return registro

    # Busca a última simulação com o hash informado.
    def buscar_por_hash(self, hash_requisicao: str) -> Optional[SimulacaoRecord]:
        for registro in reversed(self._storage):
            if registro.hash_requisicao == hash_requisicao:
                return registro
        return None

    # Lista as simulações mais recentes sem filtro.
    def listar_simulacoes(self, limite: int = 50) -> list[SimulacaoRecord]:
        return list(reversed(self._storage))[:limite]

    # Lista as simulações mais recentes de um usuário específico.
    def listar_simulacoes_por_usuario(self, usuario_id: int, limite: int = 50) -> list[SimulacaoRecord]:
        filtrados = [r for r in self._storage if r.usuario_id == usuario_id]
        return list(reversed(filtrados))[:limite]


# Representa um usuário simples em memória.
class UsuarioRecord:

    # Inicializa os dados básicos do usuário.
    def __init__(self, id: int, nome: str, email: str, senha_hash: str, senha_salt: str):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.senha_salt = senha_salt


# Representa uma sessão simples em memória.
class SessaoRecord:

    # Inicializa os dados de uma sessão autenticada.
    def __init__(self, id: int, usuario_id: int, token_hash: str):
        self.id = id
        self.usuario_id = usuario_id
        self.token_hash = token_hash


# Implementa o repositório de usuários e sessões em memória.
class InMemoryUserRepository:

    # Inicializa o armazenamento interno de usuários e sessões.
    def __init__(self):
        self._usuarios = []
        self._sessoes = []
        self._next_user_id = 1
        self._next_session_id = 1

    # Cria e armazena um novo usuário em memória.
    def criar_usuario(self, nome: str, email: str, senha_hash: str, senha_salt: str):
        usuario = UsuarioRecord(
            id=self._next_user_id,
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            senha_salt=senha_salt,
        )
        self._usuarios.append(usuario)
        self._next_user_id += 1
        return usuario

    # Busca um usuário pelo email.
    def buscar_usuario_por_email(self, email: str):
        for usuario in self._usuarios:
            if usuario.email == email:
                return usuario
        return None

    # Cria e armazena uma nova sessão em memória.
    def criar_sessao(self, usuario_id: int, token_hash: str):
        sessao = SessaoRecord(
            id=self._next_session_id,
            usuario_id=usuario_id,
            token_hash=token_hash,
        )
        self._sessoes.append(sessao)
        self._next_session_id += 1
        return sessao

    # Busca um usuário pelo id.
    def buscar_usuario_por_id(self, usuario_id: int):
        for usuario in self._usuarios:
            if usuario.id == usuario_id:
                return usuario
        return None

    # Busca o usuário vinculado ao hash do token.
    def buscar_usuario_por_token_hash(self, token_hash: str):
        for sessao in self._sessoes:
            if sessao.token_hash == token_hash:
                return self.buscar_usuario_por_id(sessao.usuario_id)
        return None