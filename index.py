import pandas as pd
import sqlite3

df = pd.read_csv("DATI_DAZEBAO_2024_06_25.csv", delimiter=";")

lista_molecole = df.drop_duplicates(subset="Molecola")['Molecola']
lista_saggi = df.drop_duplicates(subset="Saggio")['Saggio']

# Connessione al database (verrà creato se non esiste)
conn = sqlite3.connect('analisi_farmaci.db')

cursor = conn.cursor()

# for mol in lista_molecole:
#     try:
#         cursor.execute('INSERT INTO molecole (nome) VALUES (?)', (mol,))
#     except sqlite3.IntegrityError:
#         print(f"Errore nella molecola {mol}")
#         pass

for saggio in lista_saggi:
    try:
        cursor.execute('INSERT INTO saggi (saggio) VALUES (?)', (saggio,))
    except sqlite3.IntegrityError:
        print(f"Errore nella molecola {saggio}")
        pass

conn.commit()

conn.close()