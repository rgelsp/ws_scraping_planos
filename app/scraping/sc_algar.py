# %% [markdown]
# # Scraping Planos Algar
# Página do provedor: https://loja.algar.com.br/

# %% Bibliotecas ---------------------------------------------------------------
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date

# %% 1 Extração ===============================================================
provedor = "Algar"
print(f"{provedor}: Extração")

# %% 1.1 Obter lista de planos -------------------------------------------------
caminho_html = "../../data/raw/algar.html"

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()

soup = BeautifulSoup(texto_html, "html.parser")
conteiner = soup.find_all("div", class_="swiper-wrapper")[1]
planos = conteiner.find_all("div", class_="swiper-slide")
print(f"{len(planos)} cartões de planos capturados.")

# %% 1.2 Extrair informações dos planos ----------------------------------------
def raspar_plano(plano):
    velocidade = plano.find("h3").text
    preco_tag = (
        plano.find("strong", style="font-size: 24px;")
        or plano.find("div", class_="offerTile__price__main")
    )
    preco = preco_tag.text
    svas_tag = plano.find("div", class_="offerTile__offerSecondary")
    svas = svas_tag.text.strip() if svas_tag else None

    return {"velocidade": velocidade,
            "preco": preco,
            "svas": svas}

dados = []

for i in planos:
    dados_plano = raspar_plano(i)
    dados.append(dados_plano)

df = pd.DataFrame(dados)
df

# %% 2.1 Tratamento =============================================================
print(f"{provedor}: Tratamento")
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Algar"

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
df_tratado["SVAs"] = (
    df_tratado["svas"]
    .str.replace(r"[\r\n]+", " ", regex=True)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
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