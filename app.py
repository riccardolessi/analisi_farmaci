from shiny import App, reactive, render, ui
import query

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Cerca molecole",
        ui.input_select("molecole", "Seleziona la molecola", choices = []),
        ui.input_select("saggi", "Seleziona il saggio", choices = []),
        ui.input_action_button("cerca", "Cerca"),
        ui.output_text("esito_saggio"),
    ),
    ui.nav_panel(
        "Cerca saggi",
        ui.input_select("saggi_2", "Seleziona il saggio", choices = []),
        ui.input_select("molecole_2", "Seleziona la molecola", choices = []),
        ui.input_action_button("cerca_2", "Cerca"),
        ui.output_text("esito_saggio_2"),
    ),

    ui.nav_panel(
        "DB",
        ui.navset_card_tab(
            ui.nav_panel(
                "Reagenti",
                ui.input_text("input_reagenti", "Inserisci il reagente"),
                ui.input_action_button("aggiungi_reagente", "Salva")
            ),
            ui.nav_panel(
                "saggi",
                ui.tags.div(  # wrapper con altezza 100vh
                    ui.input_selectize(
                        "selectize_saggi",
                        "Seleziona il saggio",
                        multiple=False,
                        choices=[]
                    ),
                    ui.input_selectize(
                        "selectize_reagenti",
                        "Seleziona i reagenti",
                        multiple=True,
                        choices=[]
                    ),
                    ui.input_action_button("salva_reagente_saggio", "Salva"),
                    style="height: 60vh;"
                )
            )
        )
    )
    
)

def server(input, output, session):

    @reactive.effect
    @reactive.event(input.molecole)
    def _():
        x = input.molecole()
        y = query.saggi(x)
        z = {saggio[1]: saggio[2] for saggio in y}
        ui.update_select("saggi", choices = z)

    @reactive.effect
    def _():
        x = query.molecole()
        
        y = {mol[0]: mol[1] for mol in x}
        ui.update_select("molecole", choices = y)

    @render.text()
    @reactive.event(input.cerca)
    def esito_saggio():
        esito = query.esito(input.molecole(), input.saggi())
        
        print(esito)
        
        if not esito:
            return "Saggio non fatto"
        
        return f"Esito: {esito[3].capitalize()}"
    
    @reactive.effect
    def saggi_2():
        saggi = query.saggi()
        
        ui.update_select("saggi_2", choices = {saggio[0]: saggio[1] for saggio in saggi})

    @reactive.effect
    @reactive.event(input.saggi_2)
    def molecole_2():
        molecole = query.molecole(input.saggi_2())
        
        ui.update_select("molecole_2", choices = {molecola[1]: molecola[2] for molecola in molecole})

    @render.text()
    @reactive.event(input.cerca_2)
    def esito_saggio_2():
        esito = query.esito(input.molecole_2(), input.saggi_2())
        
        print(esito)
        
        if not esito:
            return "Saggio non fatto"
        
        return f"Esito: {esito[3].capitalize()}"
    

    @reactive.effect
    @reactive.event(input.aggiungi_reagente)
    def _():
        result = query.new_reagente(input.input_reagenti())
        print(result)

    @reactive.effect
    def selectize_saggi():
        saggi = query.saggi()

        ui.update_selectize("selectize_saggi", choices = {saggio[0]: saggio[1] for saggio in saggi})

    @reactive.effect
    def selectize_reagenti():
        reagenti = query.reagenti()
        
        ui.update_selectize("selectize_reagenti", choices = {reagente[0]: reagente[1] for reagente in reagenti})

    @reactive.effect
    @reactive.event(input.salva_reagente_saggio)
    def _():
        id_saggio = input.selectize_saggi()
        id_reagenti = input.selectize_reagenti()
        
        for id_reagente in id_reagenti:
            result = query.saggi_reagenti(id_saggio, id_reagente)
            print(result)

app = App(app_ui, server)