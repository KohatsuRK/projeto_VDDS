"""
Utilize dataclasses ou Pydantic. 
Aqui você define o formato do objeto cliente. 
Receber o JSON cru e transformá-lo em um objeto tipado já resolve validações estruturais, 
deixando os testes focados nas regras de negócio.

Atributos: 
-idade (int), 
-renda_mensal (float), 
-score (int), 
-nome_sujo (bool), 
-co_garantidor (bool), 
-etc.
"""

from pydantic import BaseModel, Field

class ClienteSchema(BaseModel):
    idade: int = Field(...,description="Idade do cliente em anos")
    renda_mensal: float = Field(...,description="Renda mensal líquida em reais")
    score: int = Field(...,description="Score de crédito de 0 a 1000")
    valor_imovel: float = Field(...,description="Valor do imóvel pretendido")
    nome_sujo: bool = Field(...,description="Indica se o cliente possui restrições no nome")
    co_garantidor: bool = Field(...,description="Indica se há um co-garantidor no contrato")
    anos_trabalho: int = Field(..., description="Anos de trabalho comprovados")