from shiny import ui, render, reactive, module
from riconoscimento_sottostrutture import trova_saggi_da_smiles
import pandas as pd

@module.ui
def riconoscimento_sottostrutture_ui():
    return (
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_text("input_test", "Inserisci SMILES da testare"),
                ui.input_action_button("test_button", "Testa SMILES"),
            ),
            ui.output_data_frame("test_output")
        )
    )

@module.server
def riconoscimento_sottostrutture_server(input, output, session):
    output_text = reactive.Value(pd.DataFrame())

    @reactive.effect
    @reactive.event(input.test_button)
    def _():
        test_input = input.input_test()
        saggi, success = trova_saggi_da_smiles(test_input)
        print(success)
        if success:
            # Creiamo un DataFrame dai saggi trovati
            df_saggi = pd.DataFrame(saggi, columns=["Saggi trovati"])
            
            output_text.set(df_saggi)
        else:
            output_text.set(pd.DataFrame())

    @render.data_frame
    def test_output():
        return output_text.get()