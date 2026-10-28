# %% [markdown]
# # **Scraping Planos Ouronet**
#
# Página do provedor: https://ouronet.com.br/planos/
# %%
# Bibliotecas
import pandas as pd
import numpy as np
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "OURONET"

pd.set_option('display.max_colwidth', None)
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/scraped/ouronet.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
planos = soup.find_all("div", class_="jet-listing-grid__item")

print(f"{len(planos)} cartões de planos capturados.")
# %%
# Obter informações do plano
def raspar_plano(plano):
    descricao = " ".join(
        h2.text.strip() for h2 in plano.find_all("h2")
        )
    imgs = plano.find_all("img")
    svas_urls = list({img.get("src") for img in imgs if img.get("src")})

    return {"descricao": descricao,
            "svas": svas_urls}

dados = []

for i in planos:
    try:
        dados_plano = raspar_plano(i)
        dados.append(dados_plano)
    except Exception as e:
        continue

df = pd.DataFrame(dados)
df
# %%
# Extraindo urls das imagens
df_img = (
    df["svas"]
    .explode()
    .dropna()
    .drop_duplicates()
    .reset_index(drop=True)
    .to_frame(name="URL_IMAGEM")
)
print(df_img)
# %%
import requests
import base64
import time

API_KEY = "AIzaSyA2QBWsoOKBIAg7gdp-OL2JqbK_TS3iXoU"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

def extrair_texto_imagem(url, tentativas=3):
    for tentativa in range(tentativas):
        try:
            img = requests.get(url, headers=HEADERS, timeout=15).content
            payload = {
                "requests": [{
                    "image": {"content": base64.b64encode(img).decode()},
                    "features": [{"type": "TEXT_DETECTION"}]
                }]
            }
            r = requests.post(
                f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}",
                json=payload,
                timeout=30
            )
            return r.json()["responses"][0]["fullTextAnnotation"]["text"]
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            if tentativa == tentativas - 1:
                print(f"Falhou para {url}: {e}")
                return None
            time.sleep(2)

df_img["texto"] = df_img["URL_IMAGEM"].apply(extrair_texto_imagem)
df_img
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Ouronet"

# Velocidade
df_tratado["VELOCIDADE"] = (
    df_tratado["descricao"]
    .str.extract(r"(\d+)\s*mb", flags=re.IGNORECASE)[0]
    .astype(float)
)

# Preco
df_tratado["PRECO"] = (
    df_tratado["descricao"]
    .str.extract(r"(\d+[.,]\d{2})\s*$")[0]
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# SVA
mapa_svas = dict(zip(df_img["URL_IMAGEM"], df_img["texto"]))
df_tratado["SVAs"] = (df_tratado["svas"].apply(lambda urls: ", ".join([mapa_svas[url] for url in urls if url in mapa_svas])))

df_tratado["SVAs"] = (
    df_tratado["SVAs"]
    .astype(str)
    .str.replace("\n", " ", regex=False)
)

#Seleção de colunas
df_tratado = df_tratado[["DATA", "ISP", "VELOCIDADE", "SVAs", "PRECO"]]

df_tratado = df_tratado[df_tratado["VELOCIDADE"].notna()]
print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"🟢 {provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%