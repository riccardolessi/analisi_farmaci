import json

def sostituisci_spazi_con_underscore(obj):
    if isinstance(obj, dict):
        return {k: sostituisci_spazi_con_underscore(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sostituisci_spazi_con_underscore(elem) for elem in obj]
    elif isinstance(obj, str):
        return obj.replace(" ", "_")
    else:
        return obj

# Legge il file JSON
with open("data.json", "r", encoding="utf-8") as file:
    dati = json.load(file)

# Modifica i dati
dati_modificati = sostituisci_spazi_con_underscore(dati)

# Salva il risultato
with open("dati_modificati.json", "w", encoding="utf-8") as file:
    json.dump(dati_modificati, file, ensure_ascii=False, indent=2)

print("Spazi sostituiti con underscore nel JSON.")
