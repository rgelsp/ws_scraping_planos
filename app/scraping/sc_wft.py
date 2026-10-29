# %% [markdown]
# # Scraping Planos WFT
# Página do provedor: https://www.niointernet.com.br/

# %% Bibliotecas ---------------------------------------------------------------
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date

# %% 1 Extração ===============================================================
provedor = "WFT"
print(f"{provedor}: Extração")

# %% 1.1 Obter lista de planos -------------------------------------------------
caminho_html = "../../data/raw/wft.html"

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()

soup = BeautifulSoup(texto_html, "html.parser")
conteiner = soup.find_all("div", class_="g-cols")[1]
planos = conteiner.find_all("div", class_="vc_column-inner")

# %% 1.2 Extrair informações dos planos ----------------------------------------
def raspar_plano(plano):
    velocidade = plano.find_all("p")[0].text
    preco = plano.find_all("p")[1].text
    conteiner_svas = plano.find("li", class_="w-pricing-item-feature")
    lista_svas = [i.text for i in conteiner_svas.find_all("li")]
    svas = ", ".join(i.strip() for i in lista_svas if i.strip())

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
df_tratado["ISP"] = "WFT"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"].astype(int)

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
print(f"{provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%