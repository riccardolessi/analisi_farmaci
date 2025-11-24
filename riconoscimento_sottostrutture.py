from rdkit import Chem
import pandas as pd
import sqlite3

db_path = 'analisi_farmaci.db'

def trova_saggi_da_smiles(smiles):
    """
    Cerca pattern SMARTS in una molecola data in input come SMILES.

    Parametri:
    - smiles (str): stringa SMILES della molecola da analizzare
    - lista_saggi (list[dict]): lista di dizionari, ognuno con chiavi 'smarts' e 'nome_saggio'

    Ritorna:
    - lista di nomi_saggio trovati
    """
    
    # Converte lo SMILES in un oggetto molecola RDKit
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return(f"SMILES non valido: {smiles}", False)

    risultati = []

    lista_saggi = scarica_saggi_da_db(db_path)

    # Per ogni saggio nella lista, verifica se il pattern SMARTS è presente
    for saggio in lista_saggi:
        pattern = Chem.MolFromSmarts(saggio["smarts"])
        if pattern is None:
            print(f"SMARTS non valido: {saggio['smarts']}")
            continue
        
        if mol.HasSubstructMatch(pattern):
            risultati.append(saggio["nome_saggio"].upper())

    return (risultati, True)

def scarica_saggi_da_db(db_path):
    """
    Carica i saggi dal database SQLite.

    Parametri:
    - db_path (str): percorso al file del database SQLite

    Ritorna:
    - lista di dizionari con chiavi 'smarts' e 'nome_saggio'
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT nome_saggio, smarts FROM saggi_new WHERE smarts IS NOT NULL AND smarts != ''")
    righe = cursor.fetchall()

    lista_saggi = [{"nome_saggio": row[0], "smarts": row[1]} for row in righe]

    conn.close()

    return lista_saggi