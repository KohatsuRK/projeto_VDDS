import hashlib
import secrets

class UserService:
    # Inicializa o serviço com o repositório de usuários.
    def __init__(self, repositorio):
        self.repositorio = repositorio

    # Gera o hash seguro da senha usando salt.
    def _gerar_hash_senha(self, senha: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode(),
            salt.encode(),
            100_000
        ).hex()

    # Verifica se a senha informada corresponde ao hash salvo.
    def _verificar_senha(self, senha: str, salt: str, senha_hash: str) -> bool:
        return self._gerar_hash_senha(senha, salt) == senha_hash

    # Registra um novo usuário e impede email duplicado.
    def registrar_usuario(self, nome: str, email: str, senha: str):
        existente = self.repositorio.buscar_usuario_por_email(email)
        if existente is not None:
            raise ValueError("email ja cadastrado")

        salt = secrets.token_hex(16)
        senha_hash = self._gerar_hash_senha(senha, salt)

        return self.repositorio.criar_usuario(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            senha_salt=salt,
        )

    # Realiza login e cria uma sessão com token.
    def login(self, email: str, senha: str):
        usuario = self.repositorio.buscar_usuario_por_email(email)

        if usuario is None:
            raise ValueError("credenciais invalidas")

        if not self._verificar_senha(senha, usuario.senha_salt, usuario.senha_hash):
            raise ValueError("credenciais invalidas")

        token = secrets.token_hex(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        self.repositorio.criar_sessao(
            usuario_id=usuario.id,
            token_hash=token_hash,
        )

        return {
            "token": token,
            "usuario": usuario,
        }

    # Busca o usuário associado a um token válido.
    def buscar_usuario_por_token(self, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return self.repositorio.buscar_usuario_por_token_hash(token_hash)