"""
Este arquivo conterá duas funções principais para isolar as técnicas de teste:

avaliar_credito(cliente): Retorna a string "Aprovado", "Recusado" ou "Análise Humana". 
É aqui que o Radon vai brilhar. 
Você vai construir os if/elif/else propositalmente aninhados ou compostos para gerar uma 
Complexidade Ciclomática mensurável e aplicar a tabela verdade do MC/DC.

calcular_taxa_juros(cliente): Retorna um float. 
Aqui você aplica o Fluxo de Dados (Def-Clear). 
A variável taxa_juros_base é instanciada no topo, sofre mutações (descontos por score alto, acréscimos por risco) 
e é retornada no final.
"""

from schemas import ClienteSchema
from constants import *

def avaliar_credito(cliente: ClienteSchema) -> str:
    """
    Avalia o status do crédito do cliente baseado nas regras de negócio.
    Está função foi estruturada para apresentar uma complexidade ciclomática
    mensurável e isolar a decisão booleana complexa
    """

    # 1. Validações de Fronteira Críticas (Alvos ideais para BVA)
    if cliente.idade < IDADE_MINIMA or cliente.idade > IDADE_MAXIMA:
        return "Recusado"
    
    if cliente.score < SCORE_MINIMO or cliente.score > SCORE_MAXIMO:
        return "Recusado"
    
    if cliente.nome_sujo:
        return "Recusado"
    
    # 2. Regra de Decisão Complexa (Alvo do critério MC/DC)
    # Expressão: (A E B) OU (C E D)
    # Onde:
    # A = Renda > 5000 | B = Score > 600 | C = Co-garantidor | D = Renda > 3000

    pre_aprovado = (
        (cliente.renda_mensal > RENDA_MINIMA_APROVACAO and cliente.score > SCORE_MINIMO_APROVACAO) or
        (cliente.co_garantidor and cliente.renda_mensal > RENDA_MINIMA_COM_GARANTIDOR)
    )
    
    if pre_aprovado:
        return "Aprovado"
    
    # 3. Ramificação para Decision/Branch Coverage
    # Se não foi recusado pelas regras iniciais e não atingiu a pré-aprovação automática
    return "Análise humana"

def calcular_taxa_juros(cliente: ClienteSchema) -> float:
    """
    Calcula a taxa de juros final utilizando um fluxo de dados incremental (Def-Clear).
    Mapeia o ciclo de vida da variável taxa_juros_base da definição ao uso.
    """
    taxa_juros_base = TAXA_JUROS_BASE
    # Caminhos lógicos que modificam o valor sem redefinições destrutivas
    if cliente.score > 800:
        taxa_juros_base -= DESCONTO_SCORE_EXCELENTE  # Desconto por excelente score

    elif cliente.score > DESCONTO_SCORE_BOM:
        taxa_juros_base -= 0.01  # Desconto moderado
        
    if cliente.anos_trabalho > 5:
        taxa_juros_base -= DESCONTO_ESTABILIDADE  # Desconto por estabilidade profissional
        
    if cliente.idade > 65:
        taxa_juros_base += ACRESCIMO_RISCO_IDADE  # Acréscimo por risco atuarial

    # Uso final do dado para o retorno do Oráculo de Teste
    return round(taxa_juros_base, 4)