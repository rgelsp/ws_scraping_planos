# %% [markdown]
# # **Scraping Planos WKVE Telecom**
#
# _Página do provedor: https://www.wkve.com.br/cidades/conselheiro-pena/#planos_
# %%
# Bibliotecas
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
import re
provedor = "WKVE"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/scraped/wkve.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
container_planos = soup.find("div", class_="lista-planos")
planos = container_planos.find_all("div", class_="conteudo")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    velocidade = plano.find("div", class_="quantidade").get_text(strip=True)
    preco = plano.find("div", class_="bloco-p").get_text(strip=True)
    svas = plano.find("img").get("data-src")

    return {
        "velocidade": velocidade or None,
        "preco": preco or None,
        "svas": svas
    }

df = pd.DataFrame(raspar_plano(p) for p in planos).drop_duplicates().reset_index(drop=True)
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "WKVE"

# Velocidade
df_tratado["VELOCIDADE"] = (
    df_tratado["velocidade"]
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
df_tratado["SVAs"] = df_tratado["svas"].str.extract(r"_([^_]+)\.[^.]+$")

lista = ["watch", "globoplay", "apple", "prime", "hbo", "premiere", "disney"]
padrao = re.compile("|".join(lista), flags=re.IGNORECASE)
def processar(texto):
    if pd.isna(texto):
        return texto
    achados = padrao.findall(texto)
    resto = padrao.sub("", texto).strip(" _-")
    return " ou ".join(achados) + (f" ou {resto}" if resto else "") if achados else resto

df_tratado["SVAs"] = df_tratado["SVAs"].apply(processar)

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