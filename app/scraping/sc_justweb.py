# %% [markdown]
# # **Scraping Planos Justweb**
#
# _Página do provedor: https://justweb.com.br/_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
provedor = "JUSTWEB"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/raw/justweb.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
conteiner = soup.find("div", class_="elementor-element-ffea5f6")
bloco_planos = soup.find("div", class_="elementor-element-ffea5f6")
tags_cards = bloco_planos.select('div.e-con.e-child')
planos_destaque = tags_cards[0:3] #índices 0, 1, e 2
planos_outros = [tags_cards[3], tags_cards[5], tags_cards[7]]
print(f"{len(planos_destaque)} cartões de planos destaques capturados.")
print(f"{len(planos_outros)} cartões de planos outros capturados.")
# %%
# Extrair informações dos planos
def raspar_card_destaque(card_plano):
    # VELOCIDADE
    velocidade = card_plano.find("p").get_text(strip=True)
    # VALOR
    lista_tags_valor = card_plano.find_all("h2", class_="elementor-heading-title elementor-size-default")
    lista_tags_valor_aj = [i.get_text(strip=True) for i in lista_tags_valor]
    valor = next((i.split("R$")[1] for i in lista_tags_valor_aj if "R$" in i), None)
    # SVAs
    lista_tags_svas = card_plano.find_all("div", class_="elementor-image-box-content")
    lista_svas = [i.find("h3").get_text(strip=True) for i in lista_tags_svas]
    svas = " ou ".join(lista_svas)
    # DICIONÁRIO
    return {
        "velocidade": velocidade,
        "preco": valor,
        "svas": svas
    }

def raspar_card_outros(card_plano):
    # VELOCIDADE
    velocidade = card_plano.find("h3").get_text(strip=True)
    # VALOR
    tag_valor = card_plano.find_all("p")[1].get_text(strip=True)
    valor = tag_valor.split("/")[0].split("$")[1]
    # SVAs
    svas = card_plano.find_all("p")[0].get_text(strip=True).split(":")[1].split(".")[0]
    # DICIONÁRIO
    return {
        "velocidade": velocidade,
        "preco": valor,
        "svas": svas
    }

dados_planos = []

# ITERA SOBRE A LISTA DE TAGs DE CARDS DE PLANOS
# Para cada card aplica a função raspar_card
# Adiciona uma coluna de cidade no dicionário que é retornado
# Grava o dicionário na lista "dados_planos"
for i in planos_destaque:
    infos_plano = raspar_card_destaque(i)
    dados_planos.append(infos_plano)

for i in planos_outros:
    infos_plano = raspar_card_outros(i)
    dados_planos.append(infos_plano)

df = pd.DataFrame(dados_planos)
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
#df_tratado["DATA"] = '2026-05-19'
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Justweb"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].astype(str).str.extract(r"(\d+)").astype("Int64")
df_tratado["VELOCIDADE"] = np.where(df_tratado["velocidade"].str.contains("GIGA", case=False, na=False),
                              df_tratado["VELOCIDADE"]*1000,
                              df_tratado["VELOCIDADE"] )

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+\.?\d*)")[0]
    .astype(float)
)

# SVAs
df_tratado["SVAs"] = df_tratado["svas"]

#Seleção de colunas
df_tratado = df_tratado[["DATA", "ISP", "VELOCIDADE", "SVAs", "PRECO"]]
print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"{provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%