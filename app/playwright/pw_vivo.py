from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import time

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
    html = pagina.content()

    # ---- PATH ROBUSTO (Windows-safe) ----
    base_dir = Path(__file__).resolve().parent

    path_html = (base_dir / "../../data/scraped/vivo.html").resolve()
    path_html.parent.mkdir(parents=True, exist_ok=True)

    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML salvo em: {path_html}")

    # ---- SEGUE FLUXO NORMAL ----
    pagina.get_by_role("button", name="Consultar Fibra").first.click()

    time.sleep(5)

    response = contexto.request.get(
        "https://loja.vivo.com.br/bff/unicommerceTacticalB2CBff/v1/catalogs"
    )

    data = response.json()

    path_json = (base_dir / "../../data/scraped/vivo.json").resolve()
    path_json.parent.mkdir(parents=True, exist_ok=True)

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSON salvo em: {path_json}")

    contexto.close()
    navegador.close()