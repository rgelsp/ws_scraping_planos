# %% [markdown]
# # Scraping Planos Vivo
# Página de planos do provedor: https://vivo.com.br/para-voce/produtos-e-servicos/para-casa/internet

# %% [markdown]
# ## 1 Carga

# %% Bibliotecas ---------------------------------------------------------------
import pandas as pd
from pathlib import Path
from io import StringIO
from datetime import date
import re

provedor = "VIVO"

# %% 1.1 Ler arquivo JSON ------------------------------------------------------
caminho_json = "../../data/raw/vivo.json"

if "__file__" in globals():  # .py
    texto_json = (Path(__file__).resolve().parent / caminho_json).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_json = open(caminho_json, encoding="utf-8").read()

df = pd.read_json(StringIO(texto_json))

# %% [markdown]
# ## 2 Tratamento

# %% 2.1 Tratamento =============================================================
print(f"{provedor}: Tratamento")

# Data e provedor
df["DATA"] = date.today().strftime("%Y-%m-%d")
df["ISP"] = "Vivo"

# Velocidade
df["VELOCIDADE"] = df["textoFibra"].str.extract(r"(\d+)").astype(float)
df.loc[
    df["textoFibra"].str.contains(r"giga|gb|g\b", case=False, na=False, regex=True),
    "VELOCIDADE"
] *= 1000

# SVA: cria uma lista as colunas que iniciam com "cortesiaFibra" ou "sva" ou "textoTv"
# depois concatena essas colunas
cols_sva = [c for c in df if c.startswith(("cortesiaFibra", "sva", "textoTv"))]

df["SVAs"] = df[cols_sva].apply(
    lambda row: ", ".join(row.dropna().astype(str)),
    axis=1
)

# Preço
df["PRECO"] = (
    df["total"]
    .str.replace(r"[^\d,]", "", regex=True)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# Seleção de colunas
df_tratado = df[["DATA", "ISP", "VELOCIDADE", "SVAs", "PRECO"]]
print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"{provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%