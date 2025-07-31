import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv('matrice_completa (copia).csv')
df = df.dropna(subset=['SMILES'])

desc_list = [d[0] for d in Descriptors._descList]
calc = MoleculeDescriptors.MolecularDescriptorCalculator(desc_list)

descriptor_rows = []
valid_idx = []

for i, row in df.iterrows():
    try:
        mol = Chem.MolFromSmiles(row['SMILES'])
        if mol is not None:
            desc = calc.CalcDescriptors(mol)
            descriptor_rows.append(desc)
            valid_idx.append(i)
    except Exception as e:
        print(f"Error processing SMILES {row['SMILES']}: {e}")

# Costruisci DataFrame con descrittori
desc_df = pd.DataFrame(descriptor_rows, index=valid_idx, columns=desc_list)

# === 3. Unisci descrittori con etichette (saggi) ===
df_final = pd.concat([df.loc[valid_idx].reset_index(drop=True), desc_df.reset_index(drop=True)], axis=1)

# === 4. Scegli un saggio da predire ===
# (puoi fare un ciclo su tutti più avanti)
saggi = [col for col in df.columns if col not in ["Molecola", "SMILES"]]
saggio_target = saggi[19]  # oppure scegli manualmente, es: 'ACIDO OSSALICO'

# Rimuovi righe con target mancante
df_model = df_final.dropna(subset=[saggio_target])

X = df_model[desc_list]
y = df_model[saggio_target]

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Classification report for {saggio_target} ===")
print(classification_report(y_test, y_pred))