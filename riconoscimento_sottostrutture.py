from rdkit import Chem

lista_saggi = [
    {"smarts": "[NX3](C)(C)", "nome_saggio": "AMMINE TERZIARIE (ACIDO CITRICO E ANIDRIDE ACETICA)"},
    {"smarts": "C(=O)C(=O)", "nome_saggio": "ACIDO OSSALICO (ACETATI)"},
    {"smarts": "c1ccccc1", "nome_saggio": "ACQUA DI BROMO (FENOTIAZINE)"},
    {"smarts": "[OX2H]", "nome_saggio": "OSSIDAZIONE ACQUA DI BROMO"},
    {"smarts": "[PO4]", "nome_saggio": "AgNO3 & NH4OH (FOSFATI)"},
    {"smarts": "[Cl,Br,I]", "nome_saggio": "AgNO3 (ALOGENI)"},
    {"smarts": "c1ncnc2c1ncn2", "nome_saggio": "AgNO3 (XANTINE)"},
    {"smarts": "[C]=[N]", "nome_saggio": "BASE SCHIFF (SULFAMIDICI)"},
    {"smarts": "C(=O)N", "nome_saggio": "BIURETO CuSO4 + HCl (calcio pantotenato)"},
    {"smarts": "C(=O)N", "nome_saggio": "Saggio biureto"},
    {"smarts": "[OX2H]([CX4])", "nome_saggio": "Borace & fenolftaleina (polialcoli)"},
    {"smarts": "[NX3](C)(C)", "nome_saggio": "Ammine terziarie (Bouchardat)"},
    {"smarts": "[CX3](C)(C)C(=O)[O-]", "nome_saggio": "Bouchardat in ambiente basico (lattati)"},
    {"smarts": "[CX3](C)(C)C(=O)[O-]", "nome_saggio": "Bouchardat in ambiente basico (clorbutanolo)"},
    {"smarts": "C(=O)[O-]", "nome_saggio": "CaCl2 in ambiente basico (citrati)"},
    {"smarts": "c1ccccc1[NH2]", "nome_saggio": "Chen-Kao (fenil-alchil-ammine)"},
    {"smarts": "[Br,Cl,I]", "nome_saggio": "Clorammina T & CH2Cl2 (bromuri e ioduri)"},
    {"smarts": "c1ccccc1", "nome_saggio": "Clorammina T (fenotiazine)"},
    {"smarts": "C(=O)[O-]", "nome_saggio": "Deniges & KMnO4 (citrati)"},
    {"smarts": "[NX3H2]", "nome_saggio": "Ammine primarie e NO2-arom (diazo-copulazione)"},
    {"smarts": "[NX3](C)(C)", "nome_saggio": "Ammine terziarie (Dragendorff)"},
    {"smarts": "[C;R]=O", "nome_saggio": "TTC (steroidi)"},
    {"smarts": "c1ccccc1O", "nome_saggio": "FeCl3 (alcoli aromatici, aa, salicilati)"},
    {"smarts": "c1ccccc1C(=O)C", "nome_saggio": "FeCl3 + HCl o H2SO4 (fenazone e propifenazone)"},
    {"smarts": "c1ccccc1C(=O)[O-]", "nome_saggio": "FeCl3-conc (benzoati & salicilati)"},
    {"smarts": "[CX3H1](=O)", "nome_saggio": "Ossidazione Fehling"},
    {"smarts": "[CX4H]([OH])[CX3](=O)O", "nome_saggio": "Fenton: FeSO4 + H2O2 (tartrati)"},
    {"smarts": "O=N[O-]", "nome_saggio": "Riduzione gruppo nitro (NO2-Ar)"},
    {"smarts": "[Cu]", "nome_saggio": "Beilstein (filo Cu)"},
    {"smarts": "[NX3H2]", "nome_saggio": "Ninhidrina (aminoacidi)"},
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
            risultati.append(saggio["nome_saggio"].upper())

    return (risultati, True)
