from fastapi import FastAPI

# Inicializa a aplicação
app = FastAPI(
    title="Credit Engine API",
    description="Motor de análise de crédito para os módulos Estudantil e Imobiliário",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Credit Engine API está rodando!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# TODO: Adicionar endpoints de análise de crédito aqui
# @app.post("/api/v1/credit/analyze")
# def analyze_credit(...):
#     pass