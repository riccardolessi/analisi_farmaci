from shiny import ui, render, reactive, module
import pickle
from pathlib import Path
from rdkit import Chem
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
import numpy as np

modello_ml = Path(__file__).parent.parent / "modello.pkl"

@module.ui
def predizione_ml_ui():
    return (
        ui.h2("Predizione saggio con Acqua di Bromo"),
        ui.p("Inserisci una molecola in formato SMILES per ottenere la predizione."),
        ui.input_text("smiles", "SMILES:", placeholder="es. c1ccc2c(c1)Nc3ccccc3S2"),
        ui.input_action_button("predict", "Predici"),
        ui.hr(),
        ui.output_text("result")
    )

@module.server
def predizione_ml_server(input, output, session):
    @render.text
    @reactive.event(input.predict)
    def result():
        # Trigger solo dopo il clic
        if input.predict() == 0:
            return "Inserisci uno SMILES e premi 'Predici'."

        smiles = input.smiles().strip()
        if not smiles:
            return "⚠️ Inserisci uno SMILES valido."

        # Carica il modello solo al clic
        try:
            with open(modello_ml, "rb") as f:
                print("Modello caricato con successo.")
                model = pickle.load(f)
                
        except FileNotFoundError:
            return "❌ Errore: file 'model.pkl' non trovato nella directory."

        # Converte SMILES → fingerprint
        fp = smiles_to_fp(smiles)
        if fp is None:
            return "❌ SMILES non valido."

        # Predizione
        try:
            y_pred = model.predict([fp])[0]
            if y_pred == 1:
                return f"Predizione del modello: Positivo"
            else:
                return f"Predizione del modello: Negativo"
        except Exception as e:
            return f"❌ Errore nella predizione: {e}"
        

def smiles_to_fp(smiles, radius=3, nBits=1024):
    """Converte uno SMILES in fingerprint numerico."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    gen = GetMorganGenerator(radius=radius, fpSize=nBits)
    fp = np.array(gen.GetFingerprint(mol))
    return fp