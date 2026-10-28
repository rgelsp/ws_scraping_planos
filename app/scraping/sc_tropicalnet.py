# %% [markdown]
# # **Scraping Planos TropicalNet**
#
# _Página do provedor: https://tropicalnet.com.br/planos-mg-2025/_
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
provedor = "TROPICALNET"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/scraped/tropicalnet.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
planos = soup.find_all("div", class_="elementor-col-25")
#planos = conteiner.find_all("div", class_="elementor-column")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    h4 = plano.find("h4")
    h2 = plano.find("h2")
    if h4 is None or h2 is None:
        return None

    velocidade = h4.get_text(strip=True)
    preco = h2.get_text(strip=True)
    lista_svas = plano.find_all("span", class_="elementor-icon-list-text")
    svas = ", ".join(i.get_text(strip=True) for i in lista_svas)

    return {
        "velocidade": velocidade,
        "preco": preco,
        "svas": svas
    }

dados = []

for i in planos:
    dados_plano = raspar_plano(i)
    if dados_plano:
        dados.append(dados_plano)

df = pd.DataFrame(dados)
df = df.drop_duplicates()
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Tropicalnet"

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
print(f"🟢 {provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%