import sqlite3

def setup_db():
    conn = sqlite3.connect("analisi_farmaci.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS molecole (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saggi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        saggio TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    setup_db()
