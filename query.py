import sqlite3

def molecole():
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM molecole")

    molecole = cursor.fetchall()

    return molecole

def saggi():
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saggi")

    saggi = cursor.fetchall()

    return saggi

def esito(id_molecola, id_saggio):
    conn = sqlite3.connect('analisi_farmaci.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM esiti_saggi WHERE id_molecola = ? AND id_saggio = ?", (id_molecola, id_saggio))

    esito = cursor.fetchone()

    return esito