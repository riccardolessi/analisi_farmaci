from shiny import App, reactive, render, ui
import query
import pandas as pd
from pathlib import Path
import asyncio

script_file =  Path(__file__).parent / "prova" / "www" / "script.js"

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
    ),
    ui.nav_panel(
        "associazioni",
        ui.card(
            ui.h2("Associazioni"),
            ui.output_data_frame("associazioni_df"),
        )
    ),
    ui.nav_panel(
        "Cerca reagenti",
        ui.input_select("saggi_reagenti", "Seleziona il saggio", choices = []),
        ui.input_action_button("cerca_reagenti", "Cerca"),
        ui.output_data_frame("reagenti")
    ),
    ui.nav_panel(
        "Cerca reagenti 2",
        ui.input_select("molecole_reagenti", "Seleziona la molecola", choices = []),
        ui.input_action_button("cerca_saggi", "Cerca"),
        ui.output_data_frame("saggi_reag"),
        ui.input_action_button("cerca_reagenti_mol", "Cerca"),
        ui.card(
            ui.output_ui("reagenti_mol"),
        )
    ),
    ui.nav_panel(
        "Tipologia molecola",
        ui.input_selectize("molecole_tip", "Seleziona le molecole", choices = [], multiple = True),
        ui.input_selectize("tipologia_id", "Seleziona la tipologia", choices = []),
        ui.input_action_button("salva_tipologia", "Salva"),
        ui.output_text_verbatim("text"),
    ),
    ui.nav_panel(
        "Grafico",
        ui.tags.head(
            ui.tags.script(src="https://d3js.org/d3.v7.min.js"),
        ),
        ui.HTML("<h2>Grafico Sunburst con D3.js</h2>"),
        ui.tags.div(id="chart-container"),
        ui.include_js(script_file),
    ),
    ui.nav_panel(
        "Ricerca",
        ui.card(
            ui.input_checkbox("checkbox_molecola", "Cerca le molecole"),
            ui.panel_conditional(
                "input.checkbox_molecola",
                ui.input_select("select_molecola", "Seleziona la molecola", choices = [])
            ),
            ui.input_checkbox("checkbox_saggio", "Cerca i saggi"),
            ui.panel_conditional(
                "input.checkbox_saggio",
                ui.input_select("select_saggio", "Seleziona i saggi", choices = [])
            ),
            ui.input_checkbox("checkbox_reagente", "Cerca i reagenti"),
            ui.panel_conditional(
                "input.checkbox_reagente",
                ui.input_select("select_reagente", "Seleziona i reagenti", choices = [])
            ),
            ui.input_action_button("ricerca_bottone", "Cerca"),
            
        )
    ),
)

def server(input, output, session):
    val = reactive.Value()

    @reactive.effect
    def _():
        molecole = query.molecole()
        molecole = {mol[0]: mol[1] for mol in molecole}
        saggi = query.saggi()
        saggi = {saggio[0]: saggio[1] for saggio in saggi}
        reagenti = query.reagenti()
        reagenti = {reagente[0]: reagente[1] for reagente in reagenti}

        ui.update_select("select_molecola", choices = molecole)
        ui.update_select("select_saggio", choices = saggi)
        ui.update_select("select_reagente", choices = reagenti)

    @reactive.effect
    @reactive.event(input.ricerca_bottone)
    def _():
        molecola = input.select_molecola() if input.checkbox_molecola() else None
        saggio = input.select_saggio() if input.checkbox_saggio() else None
        reagente = input.select_reagente() if input.checkbox_reagente() else None

        risultato = query.pippo(molecola, saggio, reagente)
        print(risultato)


    @reactive.effect
    async def send_data():
        data = query.esegui_query_molecole()
        
        await session.send_custom_message("d3data", data)

    @reactive.effect
    @reactive.event(input.salva_tipologia)
    def _():
        molecole = input.molecole_tip()
        tipologia = input.tipologia_id()

        result = query.nuova_tipologia(tipologia, molecole)

        ui.notification_show(
            result['message'],
            type = result['status']
        )


    @reactive.effect
    def _():
        molecole = query.molecole_tipologia()
        mol = {mol[0]: mol[1] for mol in molecole}
        ui.update_selectize("molecole_tip", choices = mol)
        
        @render.text
        def text():
            return f"Rimangono {len(molecole)} molecole"

        tipologie = query.tipologia_molecola()
        tip = {tip[0]: tip[1] for tip in tipologie}
        ui.update_selectize("tipologia_id", choices = tip)

    @render.ui
    @reactive.event(input.cerca_reagenti_mol)
    def reagenti_mol():
        messaggio = ""
        for saggio in val.get():
            id_saggio = saggio[1]
            reagenti = query.reagenti_da_saggio(id_saggio)
            
            lista_reagenti = reagenti['Reagente'].tolist()
            
            if lista_reagenti:
                messaggio += f"Il saggio {saggio[2]} richiede: "
                for mol in lista_reagenti:
                    messaggio += f"{mol}, "
            
            messaggio += "<br>"
        
        return ui.HTML(messaggio)

    @render.data_frame
    @reactive.event(input.cerca_saggi)
    def saggi_reag():
        saggi = query.saggi(input.molecole_reagenti())
        val.set(saggi)
        df = pd.DataFrame(saggi, columns=['id esito', 'id saggio', 'saggio'])
        return df


    @reactive.effect
    def molecole_reagenti():
        molecole = query.molecole()
        mol = {mol[0]: mol[1] for mol in molecole}
        ui.update_select("molecole_reagenti", choices = mol)

    @render.data_frame
    @reactive.event(input.cerca_reagenti)
    def reagenti():
        reag = query.reagenti_da_saggio(input.saggi_reagenti())
        print(reag)
        return reag


    @reactive.effect
    def saggi_reagenti():
        saggi = query.saggi()
        x = {saggio[0]: saggio[1] for saggio in saggi}
        ui.update_select("saggi_reagenti", choices = x)

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
        if input.input_reagenti() != "":
            result = query.new_reagente(input.input_reagenti())
        else:
            result = {
                "status": "failed",
                "message": "Inserisci un reagente"
            }

        if result['status'] == "success":
            ui.notification_show(
                result['message'],
                type = "message"
            )
        else:
            ui.notification_show(
                result['message'],
                type = "error"
            )

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

        if id_saggio != "" and len(id_reagenti) != 0:
            for id_reagente in id_reagenti:
                result = query.saggi_reagenti(id_saggio, id_reagente)
                
                if result['status'] == "success":
                    ui.notification_show(
                        result['message'],
                        type = "message"
                    )
                else:
                    ui.notification_show(
                        result['message'],
                        type = "error"
                    )
        else:
            ui.notification_show(
                "Compila entrambi i campi",
                type = "error"
            )

    @render.data_frame
    def associazioni_df():
        df = query.associazioni()
        
        return render.DataTable(df)

app = App(app_ui, server)