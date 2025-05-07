import sqlite3
import pandas as pd

def molecole(id_saggio = None):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()
    if id_saggio:
        id_saggio = int(id_saggio)

        cursor.execute("""
        SELECT esiti_saggi.id, molecole.id, molecole.nome FROM esiti_saggi
        JOIN molecole
        ON esiti_saggi.id_molecola = molecole.id
        WHERE esiti_saggi.id_saggio = ?
        ORDER BY molecole.nome ASC
        """, (id_saggio,))
    else:
        cursor.execute("SELECT * FROM molecole ORDER BY nome ASC")

    molecole = cursor.fetchall()

    conn.close()
    return molecole

def saggi(id_molecola = None):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()
    
    if id_molecola:
        id_molecola = int(id_molecola)

        cursor.execute("""
        SELECT esiti_saggi.id, saggi.id, saggi.saggio FROM esiti_saggi
        JOIN saggi
        ON esiti_saggi.id_saggio = saggi.id
        WHERE esiti_saggi.id_molecola = ?
        ORDER BY saggio ASC
        """, (id_molecola,))
    else:
        cursor.execute("SELECT * FROM saggi ORDER BY saggio ASC")

    saggi = cursor.fetchall()

    conn.close()
    return saggi

def esito(id_molecola, id_saggio):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM esiti_saggi WHERE id_molecola = ? AND id_saggio = ?", (id_molecola, id_saggio))

    esito = cursor.fetchone()

    conn.close()
    return esito

def new_reagente(reagente):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM reagenti WHERE reagente = ?", (reagente,))
    esistente = cursor.fetchone()

    if not esistente:
        cursor.execute("INSERT INTO reagenti (reagente) VALUES (?)", (reagente,))
    
        conn.commit()
        
        conn.close()
        return (
            {
                "status": "success",
                "message": "Reagente inserito nel DB"
            }
        )
    else:
        conn.close()
        return (
            {
                "status": "failed",
                "message": "Reagente già presente nel DB"
            }
        )
    
def reagenti():
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM reagenti ORDER BY reagente ASC")

    reagenti = cursor.fetchall()

    conn.close()
    return reagenti

def saggi_reagenti(id_saggio, id_reagente):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    try:
        cursor.execute("INSERT into saggi_reagenti (saggio_id, reagente_id) VALUES (?, ?)", (id_saggio, id_reagente))
        
        result = {
            "status": "success",
            "message": "Associazione inserita nel DB"
        }
    except:
        result = {
            "status": "failed",
            "message": "C'è stato un errore"
        }

    conn.commit()
    conn.close()

    return result

def associazioni():
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("""
    SELECT saggi_reagenti.id, saggi.saggio, reagenti.reagente
    FROM saggi_reagenti
    JOIN reagenti 
    ON saggi_reagenti.reagente_id = reagenti.id
    JOIN saggi 
    ON saggi_reagenti.saggio_id = saggi.id
    """)

    result = cursor.fetchall()

    colonne = ["id", "saggi", "reagenti"]

    df = pd.DataFrame(result, columns=colonne)

    conn.close()

    return df

def reagenti_da_saggio(id_saggio):

    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("""
        SELECT reagenti.id, reagenti.reagente 
        FROM saggi_reagenti 
        JOIN reagenti 
        ON saggi_reagenti.reagente_id = reagenti.id 
        WHERE saggi_reagenti.saggio_id = ?
    """, (id_saggio,))

    reagenti = cursor.fetchall()

    colonne = ['Id', 'Reagente']

    df = pd.DataFrame(reagenti, columns=colonne)

    return df


# QUERY PER I REAGENTI DI UN SAGGIO
# SELECT reagenti.reagente 
# FROM saggi_reagenti 
# JOIN reagenti 
# ON saggi_reagenti.reagente_id = reagenti.id 
# WHERE saggi_reagenti.saggio_id = 1

# QUERY PER I SAGGI IN CUI VIENE USATO UN REAGENTE
# SELECT saggi.saggio 
# FROM saggi_reagenti 
# JOIN saggi 
# ON saggi_reagenti.saggio_id = saggi.id 
# WHERE saggi_reagenti.reagente_id = 4;