import sqlite3
import pandas as pd
from collections import defaultdict

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
        conn.close()
        return {
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

    conn.close()

    return df


def tipologia_molecola():
    
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tipologia_molecola")

    tipologie = cursor.fetchall()
    conn.close()

    return tipologie

def nuova_tipologia(tipologia_id, molecola_ids):

    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    molecola_ids = tuple(int(x) for x in molecola_ids)

    print("tipologia_id: ", tipologia_id)
    print("molecole: ", molecola_ids)
    

    try: 
        # Genera il numero giusto di placeholder "?, ?, ?, ..."
        placeholders = ', '.join('?' for _ in molecola_ids)

        print("placeholders: ", placeholders)

        # Costruisci la query SQL in modo sicuro
        query = f"""
        UPDATE molecole
        SET tipologia_id = ?
        WHERE id IN ({placeholders})
        """
        print("query: ", query)
        params = (tipologia_id,) + molecola_ids

        # Esegui la query
        cursor.execute(query, params)
        conn.commit()

        # Chiudi la connessione
        cursor.close()
        conn.close()

        return {
            "status": "message",
            "message": "Tipologia inserita correttamente"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": e
        }


def molecole_tipologia():
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM molecole ORDER BY nome ASC")
   
    molecole = cursor.fetchall()

    molecole_filtrate = [riga for riga in molecole if riga[2] is None]

    conn.close()
    return molecole_filtrate


import sqlite3
from collections import defaultdict

def esegui_query_molecole():
    try:
        # Connessione al database
        conn = sqlite3.connect('analisi_farmaci.db')
        cursor = conn.cursor()

        # La query SQL per molecole e tipologie
        query = """
        SELECT tipologia_molecola.tipo_molecola, molecole.id, molecole.nome
        FROM molecole
        JOIN tipologia_molecola
        ON molecole.tipologia_id = tipologia_molecola.id
        ORDER BY tipologia_molecola.tipo_molecola ASC
        """
        cursor.execute(query)
        risultati = cursor.fetchall()

        # Costruisce la struttura gerarchica con i saggi
        struttura = {
            "name": "root",
            "children": []
        }

        gruppi = defaultdict(list)

        for tipologia, molecola_id, molecola_nome in risultati:
            saggi = ottieni_saggi_positivi(molecola_id)
            molecola_node = {
                "name": molecola_nome,
                "children": [{"name": s[0], "value": 1} for s in saggi] if saggi else [],
                "value": 1
            }
            gruppi[tipologia].append(molecola_node)

        for tipologia, molecole_list in gruppi.items():
            struttura["children"].append({
                "name": tipologia,
                "children": molecole_list
            })

        cursor.close()
        conn.close()
        return struttura

    except sqlite3.Error as e:
        print("Errore SQL:", e)
        return None

def ottieni_saggi_positivi(molecola_id):
    try:
        conn = sqlite3.connect('analisi_farmaci.db')
        cursor = conn.cursor()

        query = """
        SELECT saggi.saggio
        FROM esiti_saggi
        JOIN saggi ON esiti_saggi.id_saggio = saggi.id
        WHERE esiti_saggi.id_molecola = ? AND esiti_saggi.esito_saggio != 'NEGATIVO'
        """
        cursor.execute(query, (molecola_id,))
        risultati = cursor.fetchall()

        cursor.close()
        conn.close()
        return risultati

    except sqlite3.Error as e:
        print("Errore nel recupero dei saggi:", e)
        return []
    







def ricerca_complessa(molecola, saggio, reagente):
    conn = sqlite3.connect("analisi_farmaci.db")
    cursor = conn.cursor()
    query = params = None

    if molecola and not saggio and not reagente:
        cursor.execute(
        """
            SELECT esiti_saggi.id_saggio, saggi.saggio
            FROM esiti_saggi
            JOIN saggi
            ON esiti_saggi.id_saggio = saggi.id
            WHERE id_molecola = ? AND esiti_saggi.esito_saggio = 'POSITIVO'""", 
        (molecola,))
        saggi = cursor.fetchall()
        saggi_ids = [saggio[0] for saggio in saggi]
        placeholders = ",".join(["?"] * len(saggi_ids))
        cursor.execute(
        f"""
            SELECT reagenti.reagente, saggi.saggio
            FROM reagenti 
            JOIN saggi_reagenti 
            ON reagenti.id = saggi_reagenti.reagente_id
            JOIN saggi
            ON saggi_reagenti.saggio_id = saggi.id
            WHERE saggio_id IN ({placeholders})
        """, saggi_ids)
        reagenti = cursor.fetchall()
        

        risultato_saggi = pd.DataFrame([saggio[1] for saggio in saggi], columns=["Saggi"])
        risultato_reagenti = pd.DataFrame([[reagente[0], reagente[1]] for reagente in reagenti], columns=["reagente", "Saggio"])
        
        print(risultato_saggi)
        print(risultato_reagenti)

        return {
            "saggi": risultato_saggi,
            "reagenti": risultato_reagenti
        }

    elif molecola and saggio and not reagente:
        return None
    elif not molecola and saggio and not reagente:
        return None
    elif not molecola and saggio and reagente:
        return None
    
    return "Problema"

def insert_saggio_new(saggio, descrizione, schema_saggio_img, rif_saggio_temp, rif_molecola_trattata):
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO saggi_new (nome_saggio, desrizione, schema_saggio_img, rif_saggio_temp, molecola_interessata)
        VALUES (?, ?, ?, ?, ?)
        """, (saggio, descrizione, schema_saggio_img, rif_saggio_temp, rif_molecola_trattata))
        
        conn.commit()
        return {
            "status": "success",
            "message": "Saggio inserito correttamente"
        }
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        cursor.close()
        conn.close()

def saggi_new():
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saggi_new")
    saggi = cursor.fetchall()

    

    cursor.close()
    conn.close()

    return saggi
    

def get_saggio_details(saggio_id):
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saggi_new WHERE id = ?", (saggio_id,))
    saggio_details = cursor.fetchone()

    cursor.close()
    conn.close()

    print(saggio_details)
    if saggio_details:
        return {
            "id": saggio_details[0],
            "nome_saggio": saggio_details[1],
            "descrizione": saggio_details[2],
            "schema_saggio_img": saggio_details[3],
            "rif_saggio_temp": saggio_details[4],
            "molecola_trattata": saggio_details[5]
        }
    else:
        return None


def get_reagenti_saggio_new(saggio_new_id):
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT saggi.id 
    FROM saggi_new
    JOIN saggi ON saggi_new.rif_saggio_temp = saggi.id
    WHERE saggi_new.id = ?
    """, (saggio_new_id,))

    saggio_id = cursor.fetchone()

    if not saggio_id:
        cursor.close()
        conn.close()
        return []
    
    saggio_id = saggio_id[0]

    cursor.execute("""
    SELECT reagenti.reagente
    FROM saggi_reagenti
    JOIN reagenti ON saggi_reagenti.reagente_id = reagenti.id
    WHERE saggi_reagenti.saggio_id = ?
    """, (saggio_id,))

    reagenti = cursor.fetchall()

    cursor.close()
    conn.close()

    return [reagente[0] for reagente in reagenti]

# def esegui_query_molecole():
#     try:
#         # Connessione al database
#         conn = sqlite3.connect('analisi_farmaci.db')
#         cursor = conn.cursor()

#         # La query SQL
#         query = """
#         SELECT tipologia_molecola.tipo_molecola, molecole.nome
#         FROM molecole
#         JOIN tipologia_molecola
#         ON molecole.tipologia_id = tipologia_molecola.id
#         ORDER BY tipologia_molecola.tipo_molecola ASC
#         """

#         # Esegui la query
#         cursor.execute(query)

#         # Recupera tutti i risultati
#         risultati = cursor.fetchall()

#         # Chiudi la connessione
#         cursor.close()
#         conn.close()

#         raggruppati = raggruppa_molecole(risultati)

#         return raggruppati

#     except sqlite3.Error as e:
#         print("Errore SQL:", e)
#         return None


# def raggruppa_molecole(molecole_tuplas):
#     struttura = {
#         "name": "root",
#         "children": []
#     }

#     # Raggruppa le molecole per tipologia
#     gruppi = defaultdict(list)
#     for tipologia, molecola in molecole_tuplas:
#         gruppi[tipologia].append(molecola)

#     # Costruisci la struttura finale
#     for tipologia, molecole_list in gruppi.items():
#         children = [{"name": nome, "value": 1} for nome in molecole_list]
#         struttura["children"].append({
#             "name": tipologia,
#             "children": children
#         })

#     return struttura


# def prova(nome_molecola):
#     # Connessione al database
#     conn = sqlite3.connect('analisi_farmaci.db')
#     cursor = conn.cursor()

#     cursor.execute(f"SELECT id FROM molecole WHERE nome LIKE '%{nome_molecola}%'")

#     risultato = cursor.fetchone()

#     cursor.execute(f"SELECT saggi.saggio FROM esiti_saggi JOIN saggi ON esiti_saggi.id_saggio = saggi.id WHERE esiti_saggi.id_molecola = {risultato[0]} AND esiti_saggi.esito_saggio != 'NEGATIVO'")

#     saggi = cursor.fetchall()

#     # Chiudi la connessione
#     cursor.close()
#     conn.close()

#     x = []

#     for saggio in saggi:
#         x.append({"name": saggio[0], "value": 1})

#     print(x)


#     return saggi


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

# QUERY PER VEDERE TIPOLOGIA MOLECOLE E MOLECOLE
# SELECT tipologia_molecola.tipo_molecola, molecole.nome
# FROM molecole
# JOIN tipologia_molecola
# ON molecole.tipologia_id = tipologia_molecola.id
# ORDER BY tipoogia_molecola.tipo_molecola ASC

def test_ricerca_molecole_positive(rif_saggio_temp = 53):
    conn = sqlite3.connect('analisi_farmaci.db')
    cursor = conn.cursor()

    # Query parametrizzata
    query = """
    SELECT 
        m.id AS id_molecola,
        m.nome AS nome_molecola,
        sn.id AS id_saggio,
        sn.nome_saggio,
        sn.desrizione,
        sn.schema_saggio_img,
        sn.molecola_interessata,
        es.esito_saggio
    FROM esiti_saggi AS es
    JOIN saggi_new AS sn
        ON es.id_saggio = sn.rif_saggio_temp
    JOIN molecole AS m
        ON es.id_molecola = m.id
    WHERE es.esito_saggio = 'POSITIVO'
    AND sn.rif_saggio_temp = ?;
    """

    # Esegui la query con parametro
    df = pd.read_sql_query(query, conn, params=(rif_saggio_temp,))

    # Mostra il DataFrame
    print(df)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_ricerca_molecole_positive()
