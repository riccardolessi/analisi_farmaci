import importlib
import pkg_resources
from datetime import datetime
from pathlib import Path

# Dizionario dei pacchetti da controllare
packages = {
    "plotly": None,
    "shiny": None,
    "pandas": None,
    "matplotlib": None,
    "shinywidgets": None,
    "jcamp": None,
    "requests": None,
    "rdkit": None,
    "numpy": None,
    "scipy": None,
    "scikit-learn": "1.2.1",  # versione attesa
}

print("🔍 Verifica versioni pacchetti Python:\n")

# Qui salviamo le righe per il file requirements
requirements = []

for pkg, expected in packages.items():
    try:
        version = pkg_resources.get_distribution(pkg).version
        if expected:
            status = "✅ OK" if version == expected else f"⚠️ Diversa (attesa: {expected})"
        else:
            status = "✅"
        print(f"{pkg:<15} {version:<10} {status}")

        # aggiungi riga a requirements
        requirements.append(f"{pkg}=={version}")
    except Exception as e:
        print(f"{pkg:<15} ❌ Non installato ({e})")
        # segna pacchetto mancante con commento
        requirements.append(f"# {pkg} non installato")

# Scrive il file requirements_generated.txt
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
output_path = Path("requirements_generated.txt")

with output_path.open("w", encoding="utf-8") as f:
    f.write(f"# Generato automaticamente il {timestamp}\n")
    f.write("# File creato da check_versions.py\n\n")
    for line in requirements:
        f.write(line + "\n")

print(f"\n✅ Verifica completata. File generato: {output_path.resolve()}")
