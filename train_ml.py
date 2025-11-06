# ================================
# Script: train_model.py
# Addestra un modello ML da SMILES e salva in formato pickle
# ================================

import pandas as pd
import numpy as np
import pickle
from rdkit import Chem
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import accuracy_score

# ================================
# ⚙️ CONFIGURAZIONE
# ================================
CSV_FILE = "dataset.csv"  # <-- sostituisci con il tuo file CSV
TARGET_COL = "OSSIDAZIONE ACQUA DI BROMO"  # nome della colonna target
SMILES_COL = "SMILES"
MODEL_FILE = "modello.pkl"  # file finale da salvare

# ================================
# 🔬 FUNZIONE: SMILES → Fingerprint
# ================================
def smiles_to_fp(smiles, radius=3, nBits=1024):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"⚠️ Errore nella conversione SMILES: {smiles}")
        return None
    gen = GetMorganGenerator(radius=radius, fpSize=nBits)
    return np.array(gen.GetFingerprint(mol))

# ================================
# 📥 LETTURA DATI
# ================================
print("📂 Caricamento dataset...")
df = pd.read_csv(CSV_FILE, sep=";")
df = df.dropna(subset=[TARGET_COL])
print(f"✅ Dati caricati: {df.shape[0]} righe")

# ================================
# 🧩 GENERAZIONE FINGERPRINT
# ================================
print("🧬 Generazione fingerprint RDKit...")
df["Fingerprint"] = df[SMILES_COL].apply(smiles_to_fp)
df = df[df["Fingerprint"].notnull()]  # rimuove SMILES non validi

X = np.stack(df["Fingerprint"].values)
y = df[TARGET_COL].values

# ================================
# 🧠 MODELLAZIONE (Leave-One-Out CV)
# ================================
print("⚡ Addestramento modello Random Forest con LOOCV...")
clf = RandomForestClassifier(n_estimators=80, random_state=42, class_weight="balanced")

loo = LeaveOneOut()
scores = cross_val_score(clf, X, y, cv=loo)
print(f"📊 Accuracy media (LOOCV): {np.mean(scores):.3f}")

# ================================
# 🚀 ADDDESTRAMENTO FINALE E SALVATAGGIO
# ================================
clf.fit(X, y)
with open(MODEL_FILE, "wb") as f:
    pickle.dump(clf, f)

print(f"💾 Modello salvato in: {MODEL_FILE}")

# ================================
# 🧪 ESEMPIO DI TEST SU NUOVE MOLECOLE
# ================================
nuovi_smiles = [
    "C=C", "C=CC", "C=CC1=CC=CC=C1",
    "CN1C(=O)CN=C(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3",
    "C1CN(CCC1(C2=CC=C(C=C2)Cl)O)CCCC(=O)C3=CC=C(C=C3)F",
    "CCCCC(C)(C/C=C/[C@H]1[C@@H](CC(=O)[C@@H]1CCCCCCC(=O)OC)O)O",
    "C1=CC(=CC=C1N)S(=O)(=O)C2=CC=C(C=C2)N",
    "CC", "CCC", "C1=CC=CC=C1", "CO", "CC(=O)C",
    "CC(CCC1=CC=CC=C1)NCC(C2=CC(=C(C=C2)O)C(=O)N)O",
    "C1=CC=C2C(=C1)NC3=CC=CC=C3S2",
    "CN(C)CCCN1c2ccccc2Sc3ccc(Cl)cc13",
    "CN(C)CCCN1c2ccccc2Sc3ccc(cc13)N4CCN(CC4)C(F)(F)F"

]

nuovi_fp = [smiles_to_fp(smi) for smi in nuovi_smiles]
nuovi_fp = [fp for fp in nuovi_fp if fp is not None]

if nuovi_fp:
    preds = clf.predict(nuovi_fp)
    for smi, pred in zip(nuovi_smiles, preds):
        print(f"🔹 Molecola: {smi} → Predizione: {pred}")
else:
    print("⚠️ Nessuno SMILES valido per la predizione.")
