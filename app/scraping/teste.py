from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as pw:
    print("Abrindo navegador...")
    navegador = pw.chromium.launch(headless=False)
    contexto = navegador.new_context()

    print("Carregando URL...")
    pagina = contexto.new_page()
    pagina.goto("https://vivo.com.br/para-voce/produtos-e-servicos/para-casa/internet")

    print("Trocando localização e recarregando a página...")
    pagina.get_by_role("link", name="Trocar localização").click()
    pagina.get_by_role("textbox", name="Preencha com o nome da sua").click()
    pagina.get_by_role("textbox", name="Preencha com o nome da sua").fill("belo horizonte")
    pagina.get_by_role("link", name="Belo Horizonte (MG)").click()
    pagina.get_by_role("button", name="Confirmar").click()

    time.sleep(5)
    print("Clicando em 'Consultar Fibra'...")
    pagina.get_by_role("button", name="Consultar Fibra").first.click()

    print("Fazendo request da API 'catalogs'...")
    response = contexto.request.get(
        "https://loja.vivo.com.br/bff/unicommerceTacticalB2CBff/v1/catalogs"
    )

    print("Convertendo json...")
    data = response.json()
    with open("catalogs.txt", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Exportado.")
    
    # ---------------------
    contexto.close()
    navegador.close()