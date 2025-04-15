from shiny import App, reactive, render, ui
import query

app_ui = ui.page_fluid(
    ui.input_select("molecole", "Seleziona la molecola", choices = []),
    ui.input_select("saggi", "Seleziona il saggio", choices = []),
    ui.input_action_button("cerca", "Cerca"),
    ui.output_text("esito_saggio")
)

def server(input, output, session):

    @reactive.effect
    def _():
        x = query.molecole()
        
        y = {mol[0]: mol[1] for mol in x}
        ui.update_select("molecole", choices = y)


    @reactive.effect
    def _():
        x = query.saggi()
        y = {saggio[0]: saggio[1] for saggio in x}

        ui.update_select("saggi", choices = y)


    @render.text()
    @reactive.event(input.cerca)
    def esito_saggio():
        esito = query.esito(input.molecole(), input.saggi())
        
        print(esito)
        
        if not esito:
            return "Saggio non fatto"
        
        return f"Esito: {esito[3].capitalize()}"


app = App(app_ui, server)