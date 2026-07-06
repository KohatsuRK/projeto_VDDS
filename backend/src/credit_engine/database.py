import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from credit_engine.repository import CreditRepository, SimulacaoRecord

# Em produção, DATABASE_URL vem da variável de ambiente.
# Localmente, usamos SQLite no arquivo newcreditcalc.db. (antigo creditcalc.db)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./newcreditcalc.db")

# O Heroku fornece URLs PostgreSQL no formato "postgres://...",
# mas o SQLAlchemy moderno exige "postgresql://..."
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Define os argumentos extras de conexão quando o banco é SQLite.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Cria o engine principal de conexão com o banco.
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Cria a fábrica de sessões do SQLAlchemy.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define a classe base das entidades ORM.
class Base(DeclarativeBase):
    pass


# Representa a tabela de simulações persistidas no banco.
class SimulacaoORM(Base):
    """
    Modelo ORM da tabela 'simulacoes'.
    Cada instância desta classe = uma linha na tabela.
    """
    __tablename__ = "simulacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome_proponente = Column(String, nullable=False)
    status_proposta = Column(String, nullable=False)     # APROVADO | ANALISE_HUMANA | RECUSADO
    taxa_juros_aplicada = Column(Float, nullable=True)   # Null para recusados
    motivo_decisao = Column(String, nullable=False)
    data_processamento = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    hash_requisicao = Column(String, index=True, nullable=False)
    usuario_id = Column(Integer, nullable=True, index=True)


# Cria todas as tabelas do banco caso ainda não existam.
def criar_tabelas():
    Base.metadata.create_all(bind=engine)


# Abre e fecha uma sessão de banco para uso via dependência.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Implementa o repositório real de simulações com SQLAlchemy.
class SqlCreditRepository(CreditRepository):
    """
    Repositório real que persiste no banco via SQLAlchemy.
    Usado em produção e nos testes de integração.
    """

    # Inicializa o repositório com a sessão do banco.
    def __init__(self, db: Session):
        self.db = db

    # Salva uma nova simulação no banco com usuário opcional.
    def salvar_simulacao(
        self,
        nome_proponente: str,
        status_proposta: str,
        taxa_juros_aplicada: Optional[float],
        motivo_decisao: str,
        hash_requisicao: str,
        usuario_id: Optional[int] = None,
    ) -> SimulacaoRecord:
        dados = {
            "nome_proponente": nome_proponente,
            "status_proposta": status_proposta,
            "taxa_juros_aplicada": taxa_juros_aplicada,
            "motivo_decisao": motivo_decisao,
            "hash_requisicao": hash_requisicao,
        }

        if usuario_id is not None:
            dados["usuario_id"] = usuario_id

        orm_obj = SimulacaoORM(**dados)
        self.db.add(orm_obj)
        self.db.commit()
        self.db.refresh(orm_obj)
        return self._to_record(orm_obj)

    # Busca a simulação mais recente pelo hash da requisição.
    def buscar_por_hash(self, hash_requisicao: str) -> Optional[SimulacaoRecord]:
        orm_obj = (
            self.db.query(SimulacaoORM)
            .filter(SimulacaoORM.hash_requisicao == hash_requisicao)
            .order_by(SimulacaoORM.id.desc())
            .first()
        )
        return self._to_record(orm_obj) if orm_obj else None

    # Lista as últimas simulações sem filtro por usuário.
    def listar_simulacoes(self, limite: int = 50) -> list[SimulacaoRecord]:
        resultados = (
            self.db.query(SimulacaoORM)
            .order_by(SimulacaoORM.id.desc())
            .limit(limite)
            .all()
        )
        return [self._to_record(r) for r in resultados]

    # Lista as últimas simulações de um usuário específico.
    def listar_simulacoes_por_usuario(self, usuario_id: int, limite: int = 50) -> list[SimulacaoRecord]:
        resultados = (
            self.db.query(SimulacaoORM)
            .filter(SimulacaoORM.usuario_id == usuario_id)
            .order_by(SimulacaoORM.id.desc())
            .limit(limite)
            .all()
        )
        return [self._to_record(r) for r in resultados]

    # Converte o objeto ORM para o record usado pelo restante da aplicação.
    @staticmethod
    def _to_record(orm_obj: SimulacaoORM) -> SimulacaoRecord:
        return SimulacaoRecord(
            id=orm_obj.id,
            nome_proponente=orm_obj.nome_proponente,
            status_proposta=orm_obj.status_proposta,
            taxa_juros_aplicada=orm_obj.taxa_juros_aplicada,
            motivo_decisao=orm_obj.motivo_decisao,
            data_processamento=orm_obj.data_processamento,
            hash_requisicao=orm_obj.hash_requisicao,
            usuario_id=getattr(orm_obj, "usuario_id", None),
        )