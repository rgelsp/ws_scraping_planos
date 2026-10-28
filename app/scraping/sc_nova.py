# %% [markdown]
# # **Scraping Planos Nova Telecom**
#
# _Página do provedor: https://www.rnova.com.br/_
# %%
# Bibliotecas
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import date
provedor = "NOVA"
# %% [markdown]
# ## **1. Extração**
# %%
# Obter lista de planos
caminho_html = '../../data/scraped/nova.html'

if "__file__" in globals():  # .py
    texto_html = (Path(__file__).resolve().parent / caminho_html).resolve().read_text(encoding="utf-8")
else:  # .ipynb
    texto_html = open(caminho_html, encoding="utf-8").read()
soup = BeautifulSoup(texto_html, "html.parser")
container_planos = soup.find_all("ul", class_="glide__slides")[0]
planos = container_planos.find_all("li", class_="glide__slide")
print(f"{len(planos)} cartões de planos capturados.")
# %%
# Extrair informações do plano
def raspar_plano(plano):
    cartao_velocidade = plano.find("div", class_="items-center")
    velocidade = cartao_velocidade.find_all("span")[0].text

    cartao_preco = plano.find("div", class_="items-baseline")
    valor_real = cartao_preco.find_all("span")[1].text
    valor_centavos = cartao_preco.find_all("span")[2].text
    preco = valor_real + valor_centavos

    bloco_svas = plano.find("ul")
    lista_svas = bloco_svas.find_all("li")
    lista_svas_textos = [i.get_text(strip=True) for i in lista_svas]
    svas = ", ".join(lista_svas_textos)

    return {"velocidade": velocidade,
            "preco": preco,
            "svas": svas}

# Iterando sobre a lista de planos
dados = []
for plano in planos:
    item = raspar_plano(plano)
    if item:
        dados.append(item)

df = pd.DataFrame(dados)
df
# %% [markdown]
# ## **2. Tratamento**
# %%
df_tratado = df.copy()

# Data e provedor
df_tratado["DATA"] = date.today().strftime("%Y-%m-%d")
df_tratado["ISP"] = "Nova"

# Velocidade
df_tratado["VELOCIDADE"] = df_tratado["velocidade"]

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
print(df_tratado.head())

# %% 3 Carga =========================================================================
nome_arq = df_tratado["DATA"].max() + "-" + provedor + ".csv"
pasta = r"\\fileserver\arquivos\Estrategia Comercial\2. POWER BI\ECM - Radar Mercado\ScrapingPlanos"
Path(pasta).mkdir(parents=True, exist_ok=True)
df_tratado.to_csv(Path(pasta) / nome_arq, index=False)
print(f"🟢 {provedor}: Carga | {nome_arq} salvo!")

# FIM ================================================================================

# %%