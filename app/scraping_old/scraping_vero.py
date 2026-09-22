# ===========================================================================
# --------------- WEB SCRAPING - PLANOS DE INTERNET VERO --------------------
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
from datetime import datetime
import re

# ===========================================================================
# FUNÇÃO PARA OBTER O HTML DE UMA PÁGINA VIA HTTP
# ===========================================================================

def obter_html(municipio):
    # CONFIGURAÇÃO DO DRIVER
    options = Options()
    #options.add_argument("--headless")  # não abre janela
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # ACESSAR A URL
    url = "https://querovero.com.br/para-voce"
    logger.info(f"Acessando: {url}")
    driver.get(url)
    espera = WebDriverWait(driver, 5) # tempo de espera padrão

    # INICIALIZAR O SELETOR DE MUNICÍPIO
    seletor = Select(
        espera.until(
            EC.presence_of_element_located((By.ID, "dropBoxCity"))
            )
        )

    # SELECCIONAR O MUNICÍPIO
    seletor.select_by_visible_text(municipio)
    logger.info(f"Acessando página de {municipio}")

    # CLICAR EM "CONFIRMAR"
    botao_confirmar = espera.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".close-select-city-box button"))
    )
    botao_confirmar.click()
   
    # ESPERAR A PÁGINA COM O MUNICÍPIO SELECIONADO CARREGAR
    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "button.text-text-default.font-bold"),
            municipio
        )
    )

    # OBTER HTML
    html = driver.page_source
    logger.info(f"HTML de {municipio} obtido")
    driver.quit()
    logger.info(f"Navegador fechado")

    return html

# ===========================================================================
# FUNÇÃO PARA PASSEAR PELOS CARDS DE PLANOS DA PÁGINA DA CIDADE
# ===========================================================================

def raspar_html(texto_html):

    soup = BeautifulSoup(texto_html, "html.parser")

    lista_planos_tratados = []

    elementos = soup.find_all(
        "a",
        onclick=lambda x: x and "Tags.PlanCarrouselClick" in x
    )

    for el in elementos:

        onclick = el.get("onclick")

        # Captura os 8 argumentos da função.
        # O último argumento pode conter vírgulas.
        match = re.search(
            r"Tags\.PlanCarrouselClick\("
            r"'([^']*)',\s*"       # 0 - TITULO
            r"'([^']*)',\s*"       # 1
            r"'([^']*)',\s*"       # 2
            r"'([^']*)',\s*"       # 3
            r"([\d.]+),\s*"        # 4 - PRECO
            r"'([^']*)',\s*"       # 5 - VELOCIDADE
            r"'([^']*)',\s*"       # 6
            r"'([^']*)'"           # 7 - SVAs
            r"\)",
            onclick
        )

        if not match:
            continue

        partes = match.groups()

        dicionario_plano = {
            "TITULO": partes[0],
            "VELOCIDADE": partes[5],
            "PRECO": float(partes[4]),
            "SVAs": partes[7]
        }

        lista_planos_tratados.append(dicionario_plano)

    df_planos = pd.DataFrame(lista_planos_tratados)

    # Obter município
    elemento_municipio = soup.find(
        "button",
        class_=lambda c: c and "font-bold" in c
    )

    if elemento_municipio:
        df_planos["MUNICIPIO"] = elemento_municipio.get_text(strip=True)
    else:
        df_planos["MUNICIPIO"] = None

    return df_planos

# ===========================================================================
# EXTRAÇÃO, TRATAMENTO E CARGA
# ===========================================================================

def extracao():

    # MUNICIPIOS
    lista_cidades = [
        "Belo Horizonte - MG",
        "Betim - MG",
        "Contagem - MG",
        "Esmeraldas - MG",
        "Governador Valadares - MG",
        "Itabira - MG",
        "Itabirito - MG",
        "João Monlevade - MG",
        "Mariana - MG",
        "Ouro Branco - MG",
        "Ouro Preto - MG",
        "Ponte Nova - MG",
        "Ribeirão das Neves - MG",
        "Sabará - MG",
        "Santa Bárbara - MG",
        "Santa Luzia - MG",
        "Vespasiano - MG"
    ]

    # CRIA UMA LISTA ONDE SERÃO REGISTRADOS OS DADOS DAS CIDADES
    dados_cidades = []

    # ITERA SOBRE A LISTA DE URLs
    for i in lista_cidades:
        try:
            texto_html = obter_html(i)

            if texto_html:
                dados_cidade = raspar_html(texto_html)
                dados_cidades.append(dados_cidade)
                logger.info(f"Dados extraídos com sucesso para {i}.")
            else:
                logger.warning(f"Nenhum HTML retornado para {i}.")

        except Exception as e:
            logger.error(f"Erro ao processar {i}: {e}")
            print(f"Erro na cidade {i}: {e}")

        finally:
            print(100 * "=")

    # RETORNA O DATA FRAME
    # dados_cidades é uma lista de data frames
    # pd.concat() empilha os data frames
    return pd.concat(dados_cidades, ignore_index=True)

def tratamento(df):

    # Captura a data atual
    # Adiciona uma coluna com a data da coleta
    data_hoje = datetime.today().strftime("%Y-%m-%d")
    df["DATA"] = data_hoje
    logger.info("Dados tratados com sucesso.")

    return df

def carga(df):

    # EXPORTA O DATA FRAME TRATADO
    # Obtém a data atual para define o nome do arquivo
    # Salva o DataFrame em CSV com separador ","
    #nome_arquivo = "/opt/airflow/dags/planos_concorrencia/exported/vero.csv"
    nome_arquivo = "data/scraped/vero.csv"
    df.to_csv(nome_arquivo, index=False, sep=",", encoding="utf-8-sig")
    logger.info("Dados carregados com sucesso.")

# ===========================================================================
# PRINCIPAL
# ===========================================================================

def scraping_vero():
    df_extraido = extracao()
    df_tratado = tratamento(df_extraido)
    carga(df_tratado)

# ===========================================================================
# EXTRAÇÃO
# ===========================================================================

if __name__ == "__main__":
    scraping_vero()

# ===========================================================================
# FIM
# ===========================================================================