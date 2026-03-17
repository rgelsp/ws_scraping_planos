# ===========================================================================
# -------------- WEB SCRAPING - PLANOS DE INTERNET JUSTWEB ------------------
# ===========================================================================

# ===========================================================================
# BIBLIOTECAS
# ===========================================================================

import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
from loguru import logger

# ===========================================================================
# FUNÇÃO PARA OBTER O HTML DE UMA PÁGINA VIA HTTP
# ===========================================================================

def obter_html(url):

    logger.info(f"Acessando: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        response.encoding = 'utf-8'
        logger.info("HTML obtido com sucesso.")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Erro ao obter HTML de {url}")
        return None
    
# ===========================================================================
# FUNÇÃO PARA CAPTURAR DADOS DENTRO DOS CARDS DE PLANOS (SEÇÃO DE DESTAQUES)
# ===========================================================================

def raspar_card_destaque(card_plano):

    # VELOCIDADE
    velocidade = card_plano.find("p").get_text(strip=True)

    # VALOR
    lista_tags_valor = card_plano.find_all("h2", class_="elementor-heading-title elementor-size-default")
    lista_tags_valor_aj = [i.get_text(strip=True) for i in lista_tags_valor]
    valor = next((i.split("R$")[1] for i in lista_tags_valor_aj if "R$" in i), None)

    #valor = valor_string.split("$")[1]

    # SVAs
    lista_tags_svas = card_plano.find_all("div", class_="elementor-image-box-content")
    lista_svas = [i.find("h3").get_text(strip=True) for i in lista_tags_svas]
    svas = ", ".join(lista_svas)


    # RETORNAR UM DICIONÁRIOS COM AS INFORMAÇÕES DO PLANO
    return {
        "provedor": "JustWeb",
        "velocidade": velocidade,
        "valor": valor,
        "svas": svas
    }

# ===========================================================================
# FUNÇÃO PARA CAPTURAR DADOS DENTRO DOS CARDS DE PLANOS (SEÇÃO OUTROS)
# ===========================================================================

def raspar_card_outros(card_plano):

    # VELOCIDADE
    velocidade = card_plano.find("h3").get_text(strip=True)

    # VALOR
    tag_valor = card_plano.find_all("p")[1].get_text(strip=True)
    valor = tag_valor.split("/")[0].split("$")[1]

    # SVAs
    svas = card_plano.find_all("p")[0].get_text(strip=True).split(":")[1].split(".")[0]

    # RETORNAR UM DICIONÁRIOS COM AS INFORMAÇÕES DO PLANO
    return {
        "provedor": "JustWeb",
        "velocidade": velocidade,
        "valor": valor,
        "svas": svas
    }

# ===========================================================================
# FUNÇÃO PARA PASSEAR PELOS CARDS DE PLANOS DA PÁGINA DA CIDADE
# ===========================================================================

def raspar_html(texto_html, cidade):

    # TRANSFORMA O TEXTO HTML EM UM OBJETO ESTRUTURADO
    soup = BeautifulSoup(texto_html, "html.parser")


    # CAPTURA OS CARDS DE PLANOS
    # Crie uma lista de tags <li> que são os cards onde estão os planos
    bloco_planos = soup.find("div", class_="elementor-element-ffea5f6")
    tags_cards = bloco_planos.select('div.e-con.e-child')

    tags_cards_destaque = tags_cards[0:3] #índices 0, 1, e 2
    tags_cards_outros = [tags_cards[3], tags_cards[5], tags_cards[7]]

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS
    dados_planos = []

    # ITERA SOBRE A LISTA DE TAGs DE CARDS DE PLANOS
    # Para cada card aplica a função raspar_card
    # Adiciona uma coluna de cidade no dicionário que é retornado
    # Grava o dicionário na lista "dados_planos"
    for i in tags_cards_destaque:
        infos_plano = raspar_card_destaque(i)
        if infos_plano:
           infos_plano["cidade"] = cidade
           dados_planos.append(infos_plano)

    for i in tags_cards_outros:
        infos_plano = raspar_card_outros(i)
        if infos_plano:
           infos_plano["cidade"] = cidade
           dados_planos.append(infos_plano)

    # RETORNA O DATA FRAME DE PLANOS
    # dados_planos é uma lista de dicionários
    # pd.DataFrame transforma a lista de dicionários em um data frame
    return pd.DataFrame(dados_planos)

# ===========================================================================
# EXTRAÇÃO, TRATAMENTO E CARGA
# ===========================================================================

def extracao():

    # DIFINE AS CIDADES A SEREM CONSULTADAS
    lista_cidades = [
    "Belo Horizonte",
    "Betim",
    "Contagem",
    "Esmeraldas",
    "Ribeirão das Neves",
    "Santa Luzia",
    "Vespasiano"
]

    # URL (Única para todas as cidades)
    url = "https://justweb.com.br/"

    texto_html = obter_html(url)

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS DAS CIDADES
    dados_cidades = []

    # ITERA SOBRE A LISTA DE URLs
    for i in lista_cidades:
        if texto_html:
            dados_cidade = raspar_html(texto_html, cidade=i)
            dados_cidades.append(dados_cidade)
            logger.info(f"{i}: Dados extraídos com sucesso.")

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
    # nome_arquivo = "/opt/airflow/dags/planos_concorrencia/exported/justweb.csv"
    nome_arquivo = "data/scraped/justweb.csv"
    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")
    logger.info("Dados carregados com sucesso.")

# ===========================================================================
# PRINCIPAL
# ===========================================================================

def scraping_justweb():
    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

# ===========================================================================
# EXTRAÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_justweb()

# ===========================================================================
# FIM
# ===========================================================================