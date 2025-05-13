import sqlite3

def setup_db():
    conn = sqlite3.connect("analisi_farmaci.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS molecole (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
        tipologia_id INT NOT NULL
    )
    """)
    # nel db attuable tipologia_id è un text, 
    # cambiare la funzione nuova_tipologia

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saggi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saggio TEXT UNIQUE
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
        FOREIGN KEY (saggio_id) REFERENCES saggi(id) ON DELETE CASCADE,
        FOREIGN KEY (reagente_id) REFERENCES reagenti(id) ON DELETE CASCADE
    );
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

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    setup_db()
