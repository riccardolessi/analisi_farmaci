from rdkit import Chem
import pandas as pd
from shiny import App, ui, render, reactive

# Esempio: carichiamo i saggi da una tabella
# Supponiamo che sia già stata letta in un DataFrame (in realtà puoi farlo da SQL)
saggi_df = pd.DataFrame({
    'saggio': ['Tollens', 'Lucas', 'Br2 in CCl4'],
    'smiles': ['[CH]=O', 'C(C)(C)Cl', 'C=C']  # pattern riconosciuti
})

def molecola_dà_reazione(smiles_input):
    try:
        mol = Chem.MolFromSmiles(smiles_input)
        if mol is None:
            return ["Errore: SMILES non valido"]

        positivi = []
        for _, row in saggi_df.iterrows():
            saggio_mol = Chem.MolFromSmarts(row['smiles'])  # usa SMARTS se vuoi substructure
            if mol.HasSubstructMatch(saggio_mol):
                positivi.append(row['saggio'])
        return positivi if positivi else ["Nessun saggio positivo trovato"]
    except Exception as e:
        return [f"Errore durante l'analisi: {e}"]

app_ui = ui.page_fluid(
    ui.h2("Riconoscimento Saggi per Molecole Organiche"),
    ui.input_text("smiles", "Inserisci uno SMILES:"),
    ui.input_action_button("check", "Controlla Saggi"),
    ui.output_text_verbatim("risultati")
)

def server(input, output, session):
    @output
    @render.text
    @reactive.event(input.check)
    def risultati():
        smiles = input.smiles()
        if not smiles:
            return "Inserisci uno SMILES per iniziare."
        risultati = molecola_dà_reazione(smiles)
        return "\n".join(risultati)
app = App(app_ui, server)
