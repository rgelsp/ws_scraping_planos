# ===========================================================================
# --------------- WEB SCRAPING - PLANOS DE INTERNET INFORNET ----------------
# ===========================================================================

# ===========================================================================
# BIBLIOTECAS
# ===========================================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from loguru import logger

# ===========================================================================
# FUNÇÃO PARA OBTER O HTML
# ===========================================================================

def obter_html():

    url = "https://www.infornetfibra.com/planos-residencias"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        # Espera os cards carregarem
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.h-fit")))

        texto_html = driver.page_source

        return texto_html

    finally:
        driver.quit()


# ===========================================================================
# FUNÇÃO PARA EXTRAIR DADOS DE UM CARD
# ===========================================================================

def raspar_card(card_plano):

    # VELOCIDADE
    velocidade_tag = card_plano.find("h1")
    velocidade = velocidade_tag.get_text(strip=True) if velocidade_tag else None

    # VALOR
    valor_tag = card_plano.find("strong")
    valor = valor_tag.get_text(strip=True) if valor_tag else None

    # SVAs
    svas = []
    container_sva = card_plano.find(
        "div",
        class_="flex flex-row flex-wrap justify-center gap-4 mb-4"
    )

    if container_sva:
        for img in container_sva.find_all("img"):
            nome = img.get("alt") or img.get("title")
            if nome:
                svas.append(nome)

    svas = " ou ".join(svas) if svas else None

    return {
        "provedor": "InforNet",
        "velocidade": velocidade,
        "valor": valor,
        "svas": svas,
        "observacao": f"A partir de {valor}." if valor else None
    }


# ===========================================================================
# FUNÇÃO PARA PARSEAR HTML
# ===========================================================================

def raspar_html(texto_html):

    soup = BeautifulSoup(texto_html, "html.parser")

    tags_cards = soup.find_all(
        "div",
        class_="h-fit flex flex-col p-4 mb-12 rounded-2xl shadow-md bg-primary relative py-8 max-lg:mb-16"
    )

    dados_planos = []

    for card in tags_cards:
        info = raspar_card(card)
        if info:
            dados_planos.append(info)

    df = pd.DataFrame(dados_planos)

    logger.info(f"{len(df)} planos capturados.")

    return df


# ===========================================================================
# EXTRAÇÃO
# ===========================================================================

def extracao():
    html = obter_html()
    return raspar_html(html)


# ===========================================================================
# TRATAMENTO
# ===========================================================================

def tratamento(df):

    if df is None or df.empty:
        logger.warning("DataFrame vazio na etapa de tratamento.")
        return df

    # Data de coleta
    data_hoje = datetime.date.today().strftime("%Y-%m-%d")
    df["data_coleta"] = data_hoje

    # Cidades
    lista_cidades = [
        "João Monlevade",
        "Ponte Nova",
        "Rio Piracicaba"
    ]

    df_cidades = pd.DataFrame({"cidade": lista_cidades})

    # Cross join
    df = df.merge(df_cidades, how="cross")

    return df


# ===========================================================================
# CARGA
# ===========================================================================

def carga(df):

    if df is None or df.empty:
        logger.warning("Nada para salvar.")
        return

    nome_arquivo = "data/scraped/infornet.csv"

    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")

    logger.info(f"Arquivo salvo em: {nome_arquivo}")


# ===========================================================================
# PIPELINE PRINCIPAL
# ===========================================================================

def scraping_infornet():

    logger.info("Iniciando scraping InforNet...")

    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

    logger.info("Pipeline finalizado com sucesso.")


# ===========================================================================
# EXECUÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_infornet()

# ===========================================================================
# FIM
# ===========================================================================