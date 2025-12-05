from shiny import ui, render, reactive, module
from riconoscimento_sottostrutture import trova_saggi_da_smiles
import pandas as pd

# -----------------------------------------
# Definizione dell'interfaccia utente (UI)
# -----------------------------------------
def riconoscimento_sottostrutture_ui():
    return (
        ui.layout_sidebar(
            # Definizione della barra laterale (input controls)
            ui.sidebar(
                ui.input_text("smiles_input", "Inserisci SMILES da testare"),
                ui.input_action_button("testa_smiles", "Testa SMILES"),
            ),
            # Area per l'output
            ui.output_data_frame("output_saggi_trovati")
        )
    )

# -----------------------------------------
# Definizione della logica del server
# -----------------------------------------
@module.server
def riconoscimento_sottostrutture_server(input, output, session):
    saggi_output_df = reactive.Value(pd.DataFrame())

    @reactive.effect
    @reactive.event(input.testa_smiles)
    def _():
        saggi, success = trova_saggi_da_smiles(input.smiles_input())

        if success:
            # Creiamo un DataFrame dai saggi trovati
            df_saggi = pd.DataFrame(saggi, columns=["Saggi trovati"])
            saggi_output_df.set(df_saggi)
        else:
            saggi_output_df.set(pd.DataFrame())

    @render.data_frame
    def output_saggi_trovati():
        return saggi_output_df.get()