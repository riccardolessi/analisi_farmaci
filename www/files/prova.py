import json

# Parola con cui deve iniziare il campo "name"
prefisso = "flare.saggi.cluster."

# Percorso al file JSON
percorso_file = "dati_modificati.json"

# Legge il file JSON
with open(percorso_file, "r", encoding="utf-8") as f:
    dati = json.load(f)

# Filtra gli oggetti che iniziano con il prefisso
risultati = [obj["name"] for obj in dati if obj["name"].startswith(prefisso)]

# Stampa i risultati
for item in risultati:
    print(item)
