import pandas as pd
from rdkit import Chem

# Carica il dataset
df = pd.read_csv("dataset.csv")

# Assicurati che la colonna SMILES sia di tipo stringa
df = df.dropna(subset=["SMILES"]).copy()
df["SMILES"] = df["SMILES"].astype(str)

# Funzione di controllo validità
def try_parse(smi):
    try:
        mol = Chem.MolFromSmiles(smi)
        return mol is not None
    except Exception:
        return False

# Applica il controllo a tutto il dataset
df["is_valid"] = df["SMILES"].apply(try_parse)

# Seleziona gli SMILES invalidi
invalid = df[~df["is_valid"]]

# Salva o visualizza
print(f"Trovati {len(invalid)} SMILES invalidi su {len(df)}.")
invalid_smiles = invalid[["Molecola", "SMILES"]]
print(invalid_smiles)
