# %% [markdown]
# # **Scraping Planos Tim**
#
# _Página do provedor: https://www.tim.com.br/mg/internet/tim-ultrafibra_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "TIM"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/raw/tim.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
planos = soup.find_all("header", class_="header-card")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    velocidade = plano.find("h2").text
    preco = plano.find("div", class_="offer-values show").text
    beneficios = plano.find("div", class_="first-benefit-content")
    img_urls = beneficios.find_all("img", class_="streamings-image")
    svas = [i["src"] for i in img_urls]

    return {"velocidade": velocidade,
            "preco": preco,
            "svas": svas}

dados = []

for i in planos:
    dados_plano = raspar_plano(i)
    dados.append(dados_plano)

df = pd.DataFrame(dados)
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Tim"

# Velocidade
vel = df_tratado["velocidade"].str.lower()
num = vel.str.extract(r"(\d+)", expand=False).astype(float)
df_tratado["VELOCIDADE"] = np.where(
    vel.str.contains(r"giga|gb", na=False),
    num * 1000,
    num
)

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+\.?\d*)")[0]
    .astype(float)
)

# SVAs
df_tratado["SVAs"] = df_tratado["svas"].apply(
    lambda lista: ", ".join(
        [url.rsplit("/", 1)[-1] for url in lista]
    )
)

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