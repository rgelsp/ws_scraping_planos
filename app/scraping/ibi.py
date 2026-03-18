# ===========================================================================
# --------------- WEB SCRAPING - PLANOS DE INTERNET IBI ----------_----------
# ===========================================================================

# ===========================================================================
# BIBLIOTECAS
# ===========================================================================

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import pandas as pd
import datetime
from loguru import logger

# ===========================================================================
# FUNÇÃO PARA OBTER O HTML DE UMA PÁGINA VIA HTTP
# ===========================================================================

def obter_html_com_selenium(url):

    print("="*80)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(), options=options)

    logger.info(f"Acessando: {url}")
    driver.get(url)

    logger.info("Aguardando a página carregar (até 15s).")
    time.sleep(15)  # Espera fixa de 15 segundos

    html = driver.page_source
    logger.info("HTML obtido.")

    driver.quit()
    logger.info("Navegador encerrado.")

    return html

# ===========================================================================
# FUNÇÃO PARA CAPTURAR DADOS DENTRO DOS CARDS DE PLANOS
# ===========================================================================

def raspar_card(card_plano):

    # TÍTULO
    titulo = card_plano.find("h2").get_text(strip=True)

    # VALOR

    try:
        #Valor quando não há promoção
        valor = card_plano.find("div", class_= "new-card-plano__price card-plano__price").get_text(strip=True).split("/")[0]
    except AttributeError:
        #Valor quando há promoção
        valor = card_plano.find("div", class_= "new-promo card-plano__price promo").get_text(strip=True).split("/")[0]

    # PROMOÇÃO
    periodo = card_plano.find("span", class_= "new-card-plano__period card-plano__period").get_text(strip=True).split("/")[0]
    valor_depois = card_plano.find("div", class_="new-card-plano__promo card-plano__promo")
    valor_depois = valor_depois.get_text(strip=True).split("/")[0] if valor_depois else None

    # SVAs
    lista_tags_sva = card_plano.find_all("span", class_="new-card-plano__text")
    lista_string_sva = [i.get_text(strip=True) for i in lista_tags_sva]
    string_svas = next((i for i in lista_string_sva if "Aplicativos inclusos" in i), None)
    #svas = string_svas.split(": ")[1]

    # OBERVARÇÃO
    obs_1 = card_plano.find("div", class_="new-card-plano__footer1").get_text(strip=True)
    obs_2 = card_plano.find("div", class_="new-card-plano__footer2").get_text(strip=True)
    observacao = f"{obs_1} / {obs_2}"

    # RETORNAR UM DICIONÁRIOS COM AS INFORMAÇÕES DO PLANO
        # RETORNAR UM DICIONÁRIOS COM AS INFORMAÇÕES DO PLANO
    return {
        "provedor": "Ibi",
        "nome_plano": titulo,
        "valor": valor,
        "periodo": periodo,
        "valor_depois": valor_depois,
        "svas": string_svas,
        "observacao": observacao
    }

# ===========================================================================
# FUNÇÃO PARA PASSEAR PELOS CARDS DE PLANOS DA PÁGINA DA CIDADE
# ===========================================================================

def raspar_html(texto_html, cidade):

    # TRANSFORMA O TEXTO HTML EM UM OBJETO ESTRUTURADO
    soup = BeautifulSoup(texto_html, "html.parser")

    # CAPTURA OS CARDS DE PLANOS
    tags_cards = soup.find_all("li", class_="card-plano")

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS
    dados_planos = []

    # ITERA SOBRE A LISTA DE TAGs DE CARDS DE PLANOS
    # Para cada card aplica a função raspar_card
    # Adiciona uma coluna de cidade no dicionário que é retornado
    # Grava o dicionário na lista "dados_planos"
    for i in tags_cards:
        try:
            infos_plano = raspar_card(i)
            if infos_plano:
                infos_plano["cidade"] = cidade
                dados_planos.append(infos_plano)
        except:
            pass  # Ignora o erro e continua com o próximo

    # RETORNA O DATA FRAME DE PLANOS
    # dados_planos é uma lista de dicionários
    # pd.DataFrame transforma a lista de dicionários em um data frame
    return pd.DataFrame(dados_planos).drop_duplicates()

# ===========================================================================
# EXTRAÇÃO, TRATAMENTO E CARGA
# ===========================================================================

def extracao():

    # DIFINE AS CIDADES A SEREM CONSULTADAS
    # Nas urls do site, alguns nomes de cidades são separadas por "-", "_" ou ""
    # Verificar no site
    lista_cidades = [
        "ipatinga",
        "governador-valadares"
    ]

    # CRIA A LISTA DE URLs
    lista_urls = [
        f"https://ibitelecom.com.br/internet-fibra-otica-para-voce/{cidade}"
        for cidade in lista_cidades
    ]

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS DAS CIDADES
    dados_cidades = []

    # ITERA SOBRE A LISTA DE URLs
    for i in lista_urls:
        texto_html = obter_html_com_selenium(i)
        if texto_html:
            nome_cidade = i.split("voce/")[1]
            dados_cidade = raspar_html(texto_html, cidade=nome_cidade)
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
    data_hoje = datetime.date.today().strftime("%Y-%m-%d")
    df["data_coleta"] = data_hoje
    logger.info("Dados tratados com sucesso.")

    return df

def carga(df):

    # EXPORTA O DATA FRAME TRATADO
    # Obtém a data atual para define o nome do arquivo
    # Salva o DataFrame em CSV com separador ","
    #nome_arquivo = "/opt/airflow/dags/planos_concorrencia/exported/ibi.csv"
    nome_arquivo = "data/scraped/ibe.csv"
    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")
    logger.info("Dados carregados com sucesso.")

# ===========================================================================
# PRINCIPAL
# ===========================================================================

def scraping_ibi():
    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

# ===========================================================================
# EXTRAÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_ibi()

# ===========================================================================
# FIM
# ===========================================================================