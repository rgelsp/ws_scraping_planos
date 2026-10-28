# %% [markdown]
# # Scraping Planos Infornet
# Página do provedor: https://www.infornetfibra.com/planos-residencias

# %% Bibliotecas ---------------------------------------------------------------
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date

# %% 1 Extração ===============================================================
provedor = "INFORNET"
print(f"{provedor}: Extração")

# %% 1.1 Obter lista de planos -------------------------------------------------
caminho_html = "../../data/scraped/infornet.html"

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()

soup = BeautifulSoup(texto_html, "html.parser")
container_planos = soup.find("div", class_="grid-cols-4")
planos = container_planos.find_all("div", class_="h-fit")
print(f"{len(planos)} cartões de planos capturados.")

# %% 1.2 Extrair informações dos planos ----------------------------------------
def raspar_plano(plano):
    velocidade = (plano.find("h1") or {}).get_text(strip=True)
    preco = (plano.find("strong") or {}).get_text(strip=True)
    svas = " ou ".join(
        t for t in (img.get("title") for img in plano.find_all("img"))
        if t
    ) or None

    return {
        "velocidade": velocidade or None,
        "preco": preco or None,
        "svas": svas
    }

df = pd.DataFrame(raspar_plano(p) for p in planos).drop_duplicates().reset_index(drop=True)
df

# %% 2.1 Tratamento =============================================================
print(f"{provedor}: Tratamento")
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Infornet"

# Velocidade
df_tratado["VELOCIDADE"] = pd.to_numeric(df_tratado["velocidade"], errors="coerce")
df_tratado["VELOCIDADE"] = df_tratado["VELOCIDADE"].apply(
    lambda x: x * 1000 if pd.notna(x) and x < 10 else x
)
df_tratado["VELOCIDADE"] = df_tratado["VELOCIDADE"].round().astype("Int64")

# SVAs
df_tratado["SVAs"] = df_tratado["svas"]

# Preço: Substui vírgula por ponto
# Convert string em float
df_tratado["PRECO"] = (
    df_tratado["preco"]
    .str.replace(",", ".", regex=False)
    .astype(float)
)

#Seleção de colunas
df_tratado = df_tratado[["DATA", "ISP", "VELOCIDADE", "SVAs", "PRECO"]]
print(df_tratado.head(10))

print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"🟢 {provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%