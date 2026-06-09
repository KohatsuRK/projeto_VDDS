from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Credit Engine API",
    description="Motor de análise de crédito para os módulos Estudantil e Imobiliário",
    version="0.1.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, você pode trocar pelo link do seu frontend Heroku
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Credit Engine API está rodando!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}