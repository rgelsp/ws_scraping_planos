# ⚠️ EXECUTAR PELO TERMINAl ⚠️
# poetry run python app/playwright/pw_algar.py

from playwright.sync_api import sync_playwright
from pathlib import Path

with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=False)
    contexto = navegador.new_context()
    pagina = contexto.new_page()
    pagina.goto("https://loja.algar.com.br/")

    # ---- CAPTURA DO HTML ----
    html = pagina.content()

    # --- SALVANDO ARQUIVO ---
    base_dir = Path(__file__).resolve().parent
    path_html = (base_dir / "../../data/raw/algar.html").resolve()
    path_html.parent.mkdir(parents=True, exist_ok=True)
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Salvo em: {path_html}")

    contexto.close()
    navegador.close()
