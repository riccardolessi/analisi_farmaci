import sqlite3
from collections import defaultdict
import json

query = """
    SELECT saggi.saggio, reagenti.reagente FROM saggi
    JOIN saggi_reagenti ON saggi_reagenti.saggio_id = saggi.id
    JOIN reagenti ON reagenti.id = saggi_reagenti.reagente_id
"""

conn = sqlite3.connect("analisi_farmaci.db")

cursor = conn.cursor()

cursor.execute(query)

tuples = cursor.fetchall()

# Raggruppamento
molecola_dict = defaultdict(list)
for saggio, reagente in tuples:
    molecola_dict[saggio].append(reagente)

# Struttura finale
risultato = [{"nome": saggio, "children": reagenti} for saggio, reagenti in molecola_dict.items()]

print(len(risultato))

# # Trasforma in struttura desiderata
# risultato = [{"nome": f"flare.reagenti.cluster.{reagente[0]}", "children": []} for reagente in tuples]

# # Scrittura su file JSON
# with open("output.json", "w", encoding="utf-8") as f:
#     json.dump(risultato, f, indent=2, ensure_ascii=False)