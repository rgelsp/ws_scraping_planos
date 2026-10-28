import subprocess
import time
import sys
from pathlib import Path

# Caminho da pasta dos scripts
PASTA_SCRIPTS = Path(__file__).parent

# Python da venv atual
PYTHON_EXEC = sys.executable

# Nome do arquivo atual
ARQUIVO_ATUAL = Path(__file__).name

# Lista scripts .py, exceto o próprio pipeline
scripts = sorted([
    s for s in PASTA_SCRIPTS.glob("*.py")
    if s.name != ARQUIVO_ATUAL
])

for script in scripts:

    print(f"\nExecutando: {script.name}")

    try:
        resultado = subprocess.run(
            [PYTHON_EXEC, str(script)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        print(f"SUCESSO: {script.name}")

        if resultado.stdout:
            print(resultado.stdout)

    except subprocess.CalledProcessError as e:

        print(f"ERRO: {script.name}")

        if e.stderr:
            print(e.stderr)

    time.sleep(3)

print("\nExecucao finalizada.")