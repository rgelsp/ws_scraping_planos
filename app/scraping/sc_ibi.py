# %% [markdown]
# # Scraping Planos Ibi Telecom
# Página do provedor: https://ibitelecom.com.br/#planos

# %% Bibliotecas ---------------------------------------------------------------
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re

# %% 1 Extração ===============================================================
provedor = "IBI"
print(f"{provedor}: Extração")

# %% 1.1 Obter lista de planos -------------------------------------------------
caminho_html = "../../data/scraped/ibi.html"

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()

soup = BeautifulSoup(texto_html, "html.parser")
container_planos = soup.find_all("div", class_="grid")[0]
planos = container_planos.find_all("article")
print(f"{len(planos)} cartões de planos capturados.")

# %% 1.2 Extrair informações dos planos ----------------------------------------
def raspar_plano(plano):
    titulo = plano.find("h3").text
    preco = plano.find("div", class_="font-display").text
    try:
        preco_depois = plano.find("p").text
    except AttributeError:
        preco_depois = None
    return {
        "titulo": titulo,
        "preco": preco,
        "preco_depois": preco_depois
    }

dados = [raspar_plano(p) for p in planos]
df = pd.DataFrame(dados)
df = df.drop_duplicates()

df

# %% 2.1 Tratamento =============================================================
print(f"{provedor}: Tratamento")
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Ibi"

# Velocidade
df_tratado["VELOCIDADE"] = (
    df_tratado["titulo"]
    .astype(str)
    .str.extract(r"(\d+)\s*(?=mega|mb)", flags=re.IGNORECASE)[0]
    .astype("Int64")
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
    df_tratado["titulo"]
    .astype(str)
    .str.split("+", n=1)
    .str[1]
    .where(lambda x: x.notna(), pd.NA)
    .str.strip()
)

# Periodo
df_tratado["PERIODO"] = (
    df_tratado["preco_depois"]
    .str.extract(r'([\d\.,]+)')[0]
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .astype(float)
)


df_tratado["preco"].str.extract(r'(\d+)\s*meses').astype(float)

# Preco depois
df_tratado["PRECO_DEPOIS"] = (
    df_tratado["preco_depois"]
    .str.extract(r"R\$\s*([\d.,]+)")[0]
    .str.replace(".", "", regex=False)   # remove separador de milhar, se houver
    .str.replace(",", ".", regex=False)  # troca vírgula decimal por ponto
    .astype(float)
)

#Seleção de colunas
df_tratado = df_tratado[["DATA", "ISP", "VELOCIDADE", "SVAs", "PRECO", "PERIODO", "PRECO_DEPOIS"]]
print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"🟢 {provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%