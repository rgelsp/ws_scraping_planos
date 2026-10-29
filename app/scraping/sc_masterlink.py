# %% [markdown]
# # **Scraping Planos Masterlink**
#
# _Página do provedor: https://masterlinktelecom.net/_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "MASTERLINK"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/raw/masterlink.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
conteiner_planos = soup.find("div", id="planosnet")
planos = conteiner_planos.find_all("div", class_="e-con-full")
len(planos)
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    velocidade = plano.find_all("h2")[0].text
    pre_preco = plano.find_all("h2")
    preco = ".".join([i.text for i in pre_preco])
    pre_sva = plano.find_all("span", class_="elementor-icon-list-text")
    svas = ", ".join([i.text for i in pre_sva])
    return {"velocidade": velocidade,
            "preco": preco,
            "svas": svas}

dados = []

for i in planos:
    dados_plano = raspar_plano(i)
    dados.append(dados_plano)

df = pd.DataFrame(dados)
df = df[df["svas"] != ""]
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Masterlink"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].str.extract(r"(\d+\.?\d*)")

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"].str.split("$").str[1]
    .str.replace(r"\D", "", regex=True)
    .astype(float)
) / 100

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