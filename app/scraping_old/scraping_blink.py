# ===========================================================================
# -------------- WEB SCRAPING - PLANOS DE INTERNET BLINK --------------------
# ===========================================================================

# ===========================================================================
# BIBLIOTECAS
# ===========================================================================

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,  Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from loguru import logger
from datetime import date

# ===========================================================================
# FUNÇÃO PARA OBTER O HTML DE UMA PÁGINA VIA HTTP
# ===========================================================================

def obter_html(municipio):
    # CONFIGURAÇÃO DO DRIVER
    options = Options()
    #options.add_argument("--headless=new")  # Não exbir a janela
    options.add_argument("--window-size=1920,1080") # Maximizar a janela
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # ACESSAR A URL
    url = "https://www.blinktelecom.com.br/blink-fibra/"
    logger.info(f"Acessando: {url}")
    driver.get(url)
    espera = WebDriverWait(driver, 3) # Definir tempo de espera

    # INICIALIZAR O SELETOR DE MUNICÍPIO
    seletor = Select(
        espera.until(
            EC.presence_of_element_located((By.ID, "cidades-cabecalho"))
            )
        )
    
    # SELECIONAR O MUNICÍPIO
    seletor.select_by_visible_text(municipio)
    logger.info(f"Acessando página de {municipio}")
    espera

    # OBTER HTML
    html = driver.page_source
    logger.info(f"HTML de {municipio} obtido")
    driver.quit()
    logger.info(f"Navegador fechado")

    return html

# ===========================================================================
# FUNÇÃO PARA PASSEAR PELOS CARDS DE PLANOS DA PÁGINA DA CIDADE
# ===========================================================================

def raspar_html(texto_html, municipio):

    soup = BeautifulSoup(texto_html, "html.parser")
    # Selecionar as iformções brutas dos panos
    elementos = soup.select("article:has(a[href])")

    lista_planos = []

    # Iterar sobre os planos
    for i in elementos:

        botao = i.select_one("a.btn-plano-click")
        velocidade = i.select_one("span.w-post-elm-value")
        imagem = i.select_one("div.plano-imagem img")

        if botao and velocidade and imagem:

            dicionario_plano = {
                "TITULO": botao.get("href"),
                "VELOCIDADE": velocidade.get_text(strip=True),
                "URL_IMAGEM": imagem.get("src")
            }

            lista_planos.append(dicionario_plano)

    # Convter listas com informações dos planos em df
    df_planos = pd.DataFrame(lista_planos)
    df_planos = df_planos.drop_duplicates().reset_index(drop=True)
    df_planos['MUNICIPIO'] = municipio

    df_planos

    return df_planos

# ===========================================================================
# EXTRAÇÃO, TRATAMENTO E CARGA
# ===========================================================================

def extracao():

    # DIFINE AS CIDADES A SEREM CONSULTADAS
    lista_cidades = [
        "Belo Horizonte",
        "Betim",
        "Contagem",
        "Ribeirão das Neves",
        "Santa Luzia",
        "Vespasiano"
    ]

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS DAS CIDADES
    dados_cidades = []

    # ITERA SOBRE A LISTA DE URLs
    for i in lista_cidades:
        texto_html = obter_html(i)
        if texto_html:
            dados_cidade = raspar_html(texto_html=texto_html, municipio=i)
            dados_cidades.append(dados_cidade)
            logger.info("Dados extraídos com sucesso.")
            print("="*80)

    # RETORNA O DATA FRAME
    # dados_cidades é uma lista de data frames
    # pd.concat() empilha os data frames
    return pd.concat(dados_cidades, ignore_index=True)

def tratamento(df):

    # Captura a data atual
    # Adiciona uma coluna com a data da coleta
    data_hoje = date.today().strftime("%Y-%m-%d")
    df["data_coleta"] = data_hoje
    logger.info("Dados tratados com sucesso.")

    return df

def carga(df):

    # EXPORTA O DATA FRAME TRATADO
    # Obtém a data atual para define o nome do arquivo
    # Salva o DataFrame em CSV com separador ","
    #nome_arquivo = "/opt/airflow/dags/planos_concorrencia/exported/blink.csv"
    nome_arquivo = "data/raw/blink.csv"
    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")
    logger.info("Dados carregados com sucesso.")

# ===========================================================================
# PRINCIPAL
# ===========================================================================

def scraping_blink():
    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

# ===========================================================================
# EXECUÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_blink()

# ===========================================================================
# FIM
# ===========================================================================
