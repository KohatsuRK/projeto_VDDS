

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# URL onde o Streamlit está rodando
STREAMLIT_URL = "http://localhost:8501"

# Tempo máximo de espera por elementos (Streamlit reexecuta o script,
# então precisamos esperar a tela atualizar)
TIMEOUT = 20


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")   # comente para ver o browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(STREAMLIT_URL)

    # Espera o Streamlit carregar completamente
    time.sleep(3)

    yield driver

    driver.quit()


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES — encapsulam interações comuns
# ══════════════════════════════════════════════════════════════════

def esperar_streamlit_rodar(driver):
    time.sleep(2)  # margem para o rerun do Streamlit


def preencher_campo_texto(driver, texto):
    """Preenche o campo de nome (primeiro text input da página)."""
    campo = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
    )
    campo.clear()
    campo.send_keys(texto)


def clicar_botao_analisar(driver):
    """Encontra e clica no botão 'Analisar Proposta'."""
    botoes = driver.find_elements(By.TAG_NAME, "button")
    for botao in botoes:
        if "Analisar" in botao.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", botao)
            time.sleep(0.5)
            botao.click()
            return True
    return False


# ══════════════════════════════════════════════════════════════════
# E2E-1 — Fluxo de aprovação completo
# ══════════════════════════════════════════════════════════════════

def test_e2e_fluxo_aprovacao(driver):
    # Preenche o nome (os defaults do form já aprovam)
    preencher_campo_texto(driver, "Joao E2E Aprovado")
    esperar_streamlit_rodar(driver)

    # Clica em Analisar
    assert clicar_botao_analisar(driver), "Botão 'Analisar' não encontrado"

    # Espera o resultado aparecer e verifica o status APROVADO
    WebDriverWait(driver, TIMEOUT).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "APROVADO")
    )

    body = driver.find_element(By.TAG_NAME, "body").text
    assert "APROVADO" in body
    assert "Resultado da Análise" in body


# ══════════════════════════════════════════════════════════════════
# E2E-2 — Fluxo de recusa (nome sujo)
# ══════════════════════════════════════════════════════════════════

def test_e2e_fluxo_recusa_nome_sujo(driver):
    preencher_campo_texto(driver, "Maria E2E Recusada")
    esperar_streamlit_rodar(driver)

    # Marca o checkbox de nome sujo
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    if checkboxes:
        # O primeiro checkbox é o de nome sujo
        driver.execute_script("arguments[0].click();", checkboxes[0])
        esperar_streamlit_rodar(driver)

    assert clicar_botao_analisar(driver), "Botão 'Analisar' não encontrado"

    WebDriverWait(driver, TIMEOUT).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "RECUSADO")
    )

    body = driver.find_element(By.TAG_NAME, "body").text
    assert "RECUSADO" in body


# ══════════════════════════════════════════════════════════════════
# E2E-3 — Navegação e histórico
# ══════════════════════════════════════════════════════════════════

def test_e2e_navegacao_historico(driver):
    # Faz uma simulação primeiro
    preencher_campo_texto(driver, "Cliente E2E Historico")
    esperar_streamlit_rodar(driver)
    clicar_botao_analisar(driver)

    WebDriverWait(driver, TIMEOUT).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Resultado da Análise")
    )

    # Navega para o Histórico via sidebar (radio button)
    # Procura o texto "Histórico" clicável
    elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Histórico')]")
    clicou = False
    for el in elementos:
        try:
            driver.execute_script("arguments[0].click();", el)
            clicou = True
            break
        except Exception:
            continue

    assert clicou, "Opção 'Histórico' não encontrada na navegação"
    esperar_streamlit_rodar(driver)

    # Verifica que a página de histórico carregou
    WebDriverWait(driver, TIMEOUT).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Histórico de Simulações")
    )

    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Histórico de Simulações" in body