import sqlite3

# Schema allineato al database reale (analisi_farmaci.db).
# L'ordine delle colonne è vincolante: query.py legge le righe per indice
# (es. get_saggio_details usa saggio_details[0..5]), quindi cambiando l'ordine
# si rompe l'app in silenzio.

def setup_db(db_path="analisi_farmaci.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # tipologia_id è TEXT nel DB reale pur contenendo id di tipologia_molecola:
    # il JOIN funziona grazie alla conversione di affinità di SQLite.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS molecole (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        tipologia_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saggi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saggio TEXT UNIQUE
    )
    """)

    # "desrizione" è un refuso presente nel DB reale e usato da query.py:
    # rinominarlo richiede una migrazione, non basta cambiarlo qui.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saggi_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_saggio TEXT UNIQUE,
        desrizione TEXT,
        schema_saggio_img TEXT,
        rif_saggio_temp INTEGER,
        molecola_interessata TEXT,
        visualizza_dettaglio INTEGER DEFAULT 1,
        smarts TEXT,
        FOREIGN KEY (rif_saggio_temp) REFERENCES saggi(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reagenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reagente TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saggi_reagenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saggio_id INTEGER,
        reagente_id INTEGER,
        FOREIGN KEY (reagente_id) REFERENCES reagenti(id) ON DELETE CASCADE,
        FOREIGN KEY (saggio_id) REFERENCES saggi(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS esiti_saggi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_molecola INTEGER NOT NULL,
        id_saggio INTEGER NOT NULL,
        esito_saggio TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipologia_molecola (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_molecola TEXT NOT NULL
    )
    """)

    # Nel DB reale esiste anche saggi_reagenti_old, residuo di una vecchia
    # migrazione: non viene ricreata di proposito.

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    setup_db()
