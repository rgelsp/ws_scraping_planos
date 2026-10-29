# %% [markdown]
# # **Scraping Planos Super Telecom**
#
# _Página do provedor: https://superitelecom.com.br/_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "SUPER"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/raw/super.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
planos = soup.find_all("div", role="article")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    texto_imagem = plano.find("img")["alt"]

    try:
        velocidade = texto_imagem.split("Mega")[0].strip()
    except:
        velocidade = ""

    try:
        preco = texto_imagem.split("$")[1].split("por")[0].strip()
    except:
        preco = ""

    try:
        svas = texto_imagem.split("com")[1].split("por")[0].strip()
    except:
        svas = ""
        
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
df_tratado["ISP"] = "Super"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].str.extract(r"(\d+)")

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# SVAs
df_tratado["SVAs"] = df_tratado["svas"].str.replace("+", ",", regex=False)

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
