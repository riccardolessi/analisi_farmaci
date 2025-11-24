from shiny import ui, render, reactive, module

@module.ui
def cerca_saggi_ui():
    return (
        ui.input_select("saggi", "Seleziona il saggio", choices = []),
        ui.input_select("molecole", "Seleziona la molecola", choices = []),
        ui.input_action_button("cerca", "Cerca"),
        ui.output_text("esito_saggio"),
    )

@module.server
def cerca_saggi_server(input, output, session, query):
    @reactive.effect
    def saggi():
        saggi = query.saggi()
        ui.update_select("saggi", choices={s[0]: s[1] for s in saggi})

    @reactive.effect
    @reactive.event(input.saggi)
    def molecole():
        molecole = query.molecole(input.saggi())
        ui.update_select("molecole", choices={m[1]: m[2] for m in molecole})

    @render.text
    @reactive.event(input.cerca)
    def esito_saggio():
        esito = query.esito(input.molecole(), input.saggi())
        if not esito:
            return "Saggio non fatto"
        return f"Esito: {esito[3].capitalize()}"

