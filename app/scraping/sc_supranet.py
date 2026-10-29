# %% [markdown]
# # **Scraping Planos Supranet**
#
# _Página do provedor: https://supranet.com.br/_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "SUPRANET"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/raw/supranet.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
planos = soup.find_all("div", role="group")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    velocidade = plano.find_all("div", attrs={"data-e-type": "widget"})[2].text
    preco = plano.find_all("div", class_="jet-listing-dynamic-field__content")[0].text
    svas = plano.find_all("p")[1].text

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
df_tratado["ISP"] = "Supranet"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].str.extract(r"(\d+)", expand=False).astype(float)

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+\.?\d*)")[0]
    .astype(float)
)

# SVAs
df_tratado["SVAs"] = df_tratado["svas"].str.replace(" e ", ", ").str.replace(".", ", ")
df_tratado["SVAs"] = df_tratado["SVAs"].str.replace(", ", " ou ")

df_tratado["SVAs"] = np.where(df_tratado["SVAs"]=="/mês",
                              np.nan,
                              df_tratado["SVAs"])

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
