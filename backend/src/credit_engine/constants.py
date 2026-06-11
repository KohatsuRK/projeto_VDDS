"""
Constantes e parâmetros do motor de regras de crédito.
Centralizar esses valores facilita a manutenção e a criação 
de testes dinâmicos (como Análise de Valor Limite).
"""

# ==========================================
# LIMITES GERAIS (Foco: BVA e Particionamento)
# ==========================================
IDADE_MINIMA = 18
IDADE_MAXIMA = 75

SCORE_MINIMO = 0
SCORE_MAXIMO = 1000

# ==========================================
# REGRAS DE PRÉ-APROVAÇÃO (Foco: MC/DC)
# ==========================================
RENDA_MINIMA_APROVACAO = 5000.0
SCORE_MINIMO_APROVACAO = 600
RENDA_MINIMA_COM_GARANTIDOR = 3000.0

# ==========================================
# TAXAS E MODIFICADORES DE JUROS (Foco: Fluxo de Dados)
# ==========================================
TAXA_JUROS_BASE = 0.10  # 10%

# Modificadores de Score
SCORE_EXCELENTE = 800
DESCONTO_SCORE_EXCELENTE = 0.03  # -3%

SCORE_BOM = 600
DESCONTO_SCORE_BOM = 0.01  # -1%

# Modificadores de Perfil
ANOS_TRABALHO_ESTABILIDADE = 5
DESCONTO_ESTABILIDADE = 0.01  # -1%

IDADE_RISCO_ATUARIAL = 65
ACRESCIMO_RISCO_IDADE = 0.02  # +2%