import pandas as pd
import sqlite3

# Connessione al database SQLite
conn = sqlite3.connect('analisi_farmaci.db')

# Esecuzione della query SQL
query = "UPDATE saggi_new SET smarts = ? WHERE id = ?"
cursor = conn.cursor()

with open('smarts saggi.csv', 'r', encoding='utf-8') as file:
    df = pd.read_csv(file, delimiter=';')

    for index, row in df.iterrows():
        id = row['id']
        smarts = row['smarts']
        if (pd.isna(smarts) or smarts.strip() == ''):
            continue  # Salta righe con SMARTS vuoto
        print(f"Row {index + 1}: ID={id}, SMARTS={smarts}")

        try:
            cursor.execute(query, (smarts, id))
 
            print(f"Inserted row {index + 1}: ID={id}, SMARTS={smarts}")
        except sqlite3.Error as e:
            print(f"Error inserting row {index + 1}: {e}")


conn.commit()
conn.close()
