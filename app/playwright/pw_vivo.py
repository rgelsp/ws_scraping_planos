from playwright.sync_api import sync_playwright
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import parse_qs
import pandas as pd
import json
import time
import html

with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=False)
    contexto = navegador.new_context()
    pagina = contexto.new_page()

    pagina.goto("https://vivo.com.br/para-voce/produtos-e-servicos/para-casa/internet")

    pagina.get_by_role("link", name="Trocar localização").click()

    campo = pagina.get_by_role("textbox", name="Preencha com o nome da sua")
    campo.fill("belo horizonte")

    pagina.get_by_role("link", name="Belo Horizonte (MG)").click()
    pagina.get_by_role("button", name="Confirmar").click()

    pagina.wait_for_load_state("networkidle")

    # ---- CAPTURA DO HTML ----
    conteudo_html = pagina.content()

    soup = BeautifulSoup(conteudo_html, "html.parser")
    planos_na_pagina = list({
        f'https://loja.vivo.com.br/bff/unicommerceTacticalB2CBff/v1/catalogs?productId={q.get("productsIds", [""])[0]}&promotion={q.get("promotion", [""])[0]}'
        for a in soup.find_all("a", href=True)
        if "vivofibra" in a["href"]
        for q in [parse_qs(html.unescape(a["href"]).split("?")[1])]
    })

    print(f"{len(planos_na_pagina)} planos encontrados na página.")

    # ---- SEGUE FLUXO NORMAL ----
    pagina.get_by_role("link", name="Contratar Fibra + Netflix").first.click()

    time.sleep(5)

    # ---- CHAMA A API PARA CADA PLANO ----
    lista_planos = []

    for url in planos_na_pagina:
        try:
            resposta = contexto.request.get(
                url,
                headers={"referer": pagina.url}
            )
            if resposta.ok:
                dados = resposta.json()
                if dados:
                    item = dados[0] if isinstance(dados, list) else dados
                    lista_planos.append(item)
            else:
                print(f"Erro {resposta.status} ao buscar {url}")
        except Exception as e:
            print(f"Erro ao buscar {url}: {e}")

    print(f"{len(lista_planos)} planos capturados com sucesso.")

    # ---- SALVA JSON BRUTO (backup) ----
    base_dir = Path(__file__).resolve().parent
    path_json = (base_dir / "../../data/scraped/vivo.json").resolve()
    path_json.parent.mkdir(parents=True, exist_ok=True)

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(lista_planos, f, ensure_ascii=False, indent=2)

    print(f"JSON salvo em: {path_json}")

    contexto.close()
    navegador.close()

# ---- MONTA O DATAFRAME ----
df_planos = pd.DataFrame(lista_planos)
print(df_planos.shape)
df_planos.head()