from shiny import ui, render, reactive, module
import pickle
from pathlib import Path
from rdkit import Chem
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
import numpy as np

# Path al modello ML
modello_ml = Path(__file__).parent.parent / "modello.pkl"

# -----------------------------------------
# Definizione dell'interfaccia utente (UI)
# -----------------------------------------
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

# -----------------------------------------
# Definizione della logica del server
# -----------------------------------------
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
            return "Inserisci uno SMILES valido."

        # Carica il modello solo al clic
        try:
            with open(modello_ml, "rb") as f:
                model = pickle.load(f)
        except FileNotFoundError:
            return (
                f"Errore: modello '{modello_ml.name}' non trovato. "
                "Rigeneralo eseguendo train_ml.py."
            )
        except Exception as e:
            # Tipicamente un pickle salvato con una versione diversa di scikit-learn.
            return (
                f"Errore nel caricamento del modello ({type(e).__name__}: {e}). "
                "Rigenera il modello eseguendo train_ml.py con l'ambiente corrente."
            )

        # Converte SMILES → fingerprint
        fp = smiles_to_fp(smiles)
        if fp is None:
            return "SMILES non valido."

        # Predizione
        try:
            y_pred = model.predict([fp])[0]

            # Probabilità per entrambe le classi
            proba = model.predict_proba([fp])[0]
            confidence = [round(x * 100, 2) for x in proba]

            if y_pred == 1:
                return f"Predizione del modello: Positivo ({confidence[1]}%)"
            else:
                return f"Predizione del modello: Negativo ({confidence[0]}%)"
        except Exception as e:
            return f"Errore nella predizione: {e}"
        

def smiles_to_fp(smiles: str, radius: int=3, nBits: int=1024):
    """
    Converte una stringa SMILES in un Morgan Fingerprint numerico di un dato raggio e dimensione.

    Args:
        smiles: La stringa SMILES della molecola.
        radius: Il raggio del fingerprint di Morgan (Esempio, 2 o 3).
        n_bits: La dimensione del fingerprint (numero di bit).

    Returns:
        Un array numpy (il fingerprint) se la conversione ha successo, altrimenti None.
    """

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    fingerprint_generator = GetMorganGenerator(radius=radius, fpSize=nBits)
    fingerprint = np.array(fingerprint_generator.GetFingerprint(mol))
    return fingerprint