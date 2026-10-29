import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError


# Lista de CEPs
df_ceps = pd.read_csv("ceps.csv", dtype=str)

def consultar_cep(page, cep):

    try:

        page.goto("https://www.niointernet.com.br/")

        page.locator("input[name='banner-input-cep']").fill(cep)
        page.get_by_role("button", name="Seta para a direita").click()

        page.wait_for_url(
            lambda url: "fibra-" in url,
            timeout=5000
        )

        url = page.url

        if "fibra-disponivel" in url:
            status = "Disponível"
        elif "fibra-indisponivel" in url:
            status = "Indisponível"
        else:
            status = "Não identificado"

    except TimeoutError:
        url = page.url
        status = "Timeout"

    return {
        "cep": cep,
        "status": status,
        "url": url
    }


def run(df_ceps):

    resultados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for cep in df_ceps["cep"]:

            print(f"Consultando {cep}...")

            resultado = consultar_cep(page, cep)

            print(resultado)

            resultados.append(resultado)

        context.close()
        browser.close()

    return pd.DataFrame(resultados)


if __name__ == "__main__":

    df_resultado = run(df_ceps)

    print("\nResultado:")
    print(df_resultado)

    # Salva em CSV
    df_resultado.to_csv("resultado_ceps_nio.csv", index=False)