# %% [markdown]
# # **Scraping Planos Ultranet**
#
# _Página do provedor: https://ultra.psi.br/home/_
# %%
# Bibliotecas
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
provedor = "ULTRANET"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/scraped/ultranet.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
container_planos = soup.find("div", id="painel-planos")
planos = container_planos.find_all("article")
print(f"{len(planos)} cartões de planos capturados.")

planos
# %%
# Extrair informações dos planos
def raspar_plano(plano):
    velocidade = plano.find_all("h3")[0].text
    preco = plano.find_all("p")[1].text
    svas = plano.find_all("p")[2].text

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
df_tratado["ISP"] = "Ultranet"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].str.extract(r"(\d+)")

# SVAs
df_tratado["SVAs"] = df_tratado["svas"]

# PRECO
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+\.?\d*)")[0]
    .astype(float)
)

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