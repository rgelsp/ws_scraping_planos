# ===========================================================================
# --------------- WEB SCRAPING - PLANOS DE INTERNET CLARO --------------------
# ===========================================================================

# ===========================================================================
# BIBLIOTECAS
# ===========================================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from loguru import logger

# ===========================================================================
# FUNÇÃO PARA OBTER O JSON DE PLANOS DA PÁGINA WEB
# ===========================================================================

def obter_json(cidade):

    url = "https://www.claro.com.br/api/mind"
    #https://www.claro.com.br/internet/banda-larga/mg/itabira

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.claro.com.br",
        "Referer": "https://www.claro.com.br/",
        "User-Agent": "Mozilla/5.0"
    }

    # CORPO DA REQUISIÇÃO
    payload = {
        "city": cidade,
        "uf": "mg",
        "type": "todos",
        "environment": "person",
        "comboType": "single",
        "internetIds": None
    }

    # REQUISIÇÃO POST
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"{cidade}: JSON extraído com sucuesso.")

    # RETORNA O JSON DE PLANOS DA CIDADE
    return response.json()

# ===========================================================================
# FUNÇÃO PARA CAPTURAR DADOS DENTRO DE CADA PLANO
# ===========================================================================

def raspar_card(card_plano):

    # NOME DO PLANO
    nome_plano = card_plano["mainOffer"]["title"]

    # VELOCIDADE
    string_velocidade = card_plano["modalData"][1]["modalContent"]["text_rich"]["content"]
    soup = BeautifulSoup(string_velocidade, "html.parser")
    velocidade = soup.find("strong").next_sibling.strip()

    # VALOR
    valor = card_plano["price"]["priceData"][0]["price"]

    # PERÍODO PROMOCIONAL
    periodo_promo = card_plano["price"]["priceData"][0]["period"]

    # VALOR APÓS PERÍODO PROMOCIONAL
    vr_pos_promo = card_plano["price"]["priceData"][0]["suffix"] #.split("R$ ")[1]

    # SVA
    lista_svas = [b["alt"] for b in card_plano["mainOffer"]["brandArea"]["brands"]["brands"]]
    svas = ", ".join(lista_svas)
    
    # RETORNAR UM DICIONÁRIOS COM AS INFORMAÇÕES DO PLANO
    return {
        "provedor": "Claro",
        "nome_plano": nome_plano,
        "velocidade": velocidade,
        "valor": valor,
        "periodo_promo": periodo_promo,
        "vr_pos_promo": vr_pos_promo,
        "svas": svas
    }

# ===========================================================================
# FUNÇÃO PARA PASSEAR PELOS PLANOS DO JSON DA CIDADE
# ===========================================================================

def raspar_json(json_planos, cidade):

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS
    dados_planos = []

    # ITERA SOBRE A LISTA DE DE PLANOS
    # Para cada plano aplica a função raspar_card
    # Grava o dicionário na lista "dados_planos"
    for i in json_planos:
        infos_plano = raspar_card(i)
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
        "belo-horizonte",
        "contagem",
        "governador-valadares",
        "ipatinga",
        "itabira",
        "ribeirao-das-neves",
        "sabara",
        "santa-luzia",
        "vespasiano",
        "ouro preto",
        "mariana",
        "betim",
        "ponte-nova",
        "joao-monlevade"
    ]

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS DAS CIDADES
    dados_cidades = []

    # ITERA SOBRE A LISTA DE CIDADES
    for i in lista_cidades:
        json_planos = obter_json(i)
        if json_planos:
            dados_cidade = raspar_json(json_planos, cidade = i)
            dados_cidades.append(dados_cidade)
            logger.info(f"{i}: dados extraídos com sucesso.")
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
    #nome_arquivo = "/opt/airflow/dags/planos_concorrencia/exported/claro.csv"
    nome_arquivo = "data/raw/claro.csv"
    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")
    logger.info("Dados carregados com sucesso.")

# ===========================================================================
# PRINCIPAL
# ===========================================================================

def scraping_claro():
    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

# ===========================================================================
# EXECUÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_claro()

# ===========================================================================
# FIM
# ===========================================================================
