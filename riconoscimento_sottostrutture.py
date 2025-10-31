from rdkit import Chem

lista_saggi = [
    {"smarts": "C=O", "nome_saggio": "Gruppo carbonilico"},
    {"smarts": "N", "nome_saggio": "Gruppo amminico"},
    {"smarts": "c1ccccc1", "nome_saggio": "Anello benzenico"},
]

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

    # Per ogni saggio nella lista, verifica se il pattern SMARTS è presente
    for saggio in lista_saggi:
        pattern = Chem.MolFromSmarts(saggio["smarts"])
        if pattern is None:
            print(f"SMARTS non valido: {saggio['smarts']}")
            continue
        
        if mol.HasSubstructMatch(pattern):
            risultati.append(saggio["nome_saggio"])

    return (risultati, True)
