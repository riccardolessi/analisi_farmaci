from shiny import App, reactive, render, ui
import query
import pandas as pd
from pathlib import Path
import asyncio
from pathlib import Path
from riconoscimento_sottostrutture import trova_saggi_da_smiles

script_file =  Path(__file__).parent / "prova" / "www" / "script.js"
script_file_2 = Path(__file__).parent / 'www' / 'app_loader.js'

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
        "Cerca reagenti",
        ui.input_select("molecole_reagenti", "Seleziona la molecola", choices = []),
        ui.input_action_button("cerca_saggi", "Cerca"),
        ui.output_data_frame("saggi_reag"),
        ui.input_action_button("cerca_reagenti_mol", "Cerca"),
        ui.card(
            ui.output_ui("reagenti_mol"),
        )
    ),
    ui.nav_panel(
        "Grafico a torta",
        ui.tags.head(
            ui.tags.script(src="https://d3js.org/d3.v7.min.js"),
        ),
        ui.HTML("<h2>Grafico Sunburst con D3.js</h2>"),
        ui.tags.div(id="chart-container"),
        ui.include_js(script_file),
    ),
    ui.nav_panel(
        "Dettaglio saggi",
        ui.page_navbar(
            ui.nav_panel(
                "Saggi esistenti",
                ui.input_select("select_saggi_esistenti", "Saggi esistenti", choices=[]),
                ui.input_action_button("visualizza_saggio", "Visualizza"),
                ui.input_action_button("elimina_saggio", "Elimina"),
                ui.card(
                    ui.output_text("saggio_details_nome_saggio"),
                    ui.output_image("saggio_details_schema_saggio_img"),
                    ui.br(),
                    ui.output_ui("saggio_details_descrizione_saggio"),
                    ui.br(),
                    ui.output_text("reagenti_saggio"),
                    ui.br(),
                    ui.output_text("molecola_trattata"),
                ),
            )
        )
    ),
    ui.nav_panel(
        "prova ml",
        ui.input_text("input_test", "Input di prova"),
        ui.input_action_button("test_button", "Esegui test"),
        ui.output_text("test_output")
    )
)

def server(input, output, session):
    val = reactive.Value()
    output_text = reactive.Value("")

    @render.text
    def test_output():
        return output_text.get()
    
    @reactive.effect
    @reactive.event(input.test_button)
    def _():
        test_input = input.input_test()
        saggi, success = trova_saggi_da_smiles(test_input)
        print(saggi, success)
        if success:
            output_text.set(f"Saggi trovati: {', '.join(saggi)}")
        else:
            output_text.set(saggi)

    @reactive.effect
    @reactive.event(input.visualizza_saggio)
    def visualizza_saggio():
        saggio_id = input.select_saggi_esistenti()
        if not saggio_id:
            ui.notification_show("Seleziona un saggio esistente", type="error")
            return
        
        try:
            saggio_details = query.get_saggio_details(saggio_id)
            if not saggio_details:
                ui.notification_show("Saggio non trovato", type="error")
                return
            
            @render.text
            def saggio_details_nome_saggio():
                return saggio_details['nome_saggio']
            
            @render.image
            def saggio_details_schema_saggio_img():
                img = str(Path(__file__).parent / "assets" / "img_saggi" / saggio_details['schema_saggio_img']) if saggio_details['schema_saggio_img'] else None
                if img is None:
                    return None
                return {
                    "src": img,
                    "width": "600px"
                }
            
            @render.ui
            def saggio_details_descrizione_saggio():
                return ui.HTML(saggio_details['descrizione'].replace("\n", "<br>"))
            
            @render.text
            def reagenti_saggio():
                reagenti = query.get_reagenti_saggio_new(saggio_id)
                if not reagenti:
                    return "Nessun reagente associato a questo saggio."
                return "Reagenti associati: " + ", ".join(reagenti)
            
            @render.text
            def molecola_trattata():
                molecola_trattata = saggio_details.get('molecola_trattata')
                if not molecola_trattata:
                    return "Nessuna molecola trattata associata a questo saggio."
                return f"Molecola trattata: {molecola_trattata}"

        except Exception as e:
            ui.notification_show(f"Errore durante il recupero del saggio: {e}", type="error")

    # Funzione per popolare il select con i saggi esistenti
    @reactive.effect
    def select_saggi_esistenti():
        # Popola il select con i saggi esistenti
        saggi = query.saggi_new()
        choices = {saggio[0]: saggio[1] for saggio in saggi}
        ui.update_select("select_saggi_esistenti", choices=choices)

    @reactive.effect
    @reactive.event(input.salva_saggio)
    def salva_saggio():
        nome = input.nome_saggio()
        descrizione = input.descrizione_saggio()
        schema = input.schema_saggio_img()
        rif_saggio_temp = input.rif_saggio_temp()
        rif_molecola_trattata = input.riferimento_molecola_trattata()

        if not nome or not descrizione or not schema:
            ui.notification_show("Compila tutti i campi", type="error")
            return

        try:
            result = query.insert_saggio_new(nome, descrizione, schema, rif_saggio_temp, rif_molecola_trattata)
            ui.notification_show(result.get("message", "Operazione completata"), type=result.get("status", "info"))
        except Exception as e:
            ui.notification_show(f"Errore durante il salvataggio: {e}", type="error")

    @reactive.effect
    def rif_saggio_temp():
        # Popola il select con i saggi esistenti
        saggi = query.saggi()
        choices = {saggio[0]: saggio[1] for saggio in saggi}
        ui.update_select("rif_saggio_temp", choices=choices)

    # Funzione per gestire la ricerca nella tab Ricerca
    @reactive.effect
    @reactive.event(input.checkbox_molecola, input.checkbox_saggio, input.checkbox_reagente)
    def _():
        molecola = input.checkbox_molecola()
        saggio = input.checkbox_saggio()
        reagente = input.checkbox_reagente()
        visualizza_log_message = True # Debug

        # Casi possibili → output choices
        cases = {
            (True, False, False): (["Saggi", "Reagenti"], "checkbox molecola"),
            (True, True, False): (["Reagenti"], "checkbox molecola e saggio"),
            (False, True, False): (["Molecole", "Reagenti"], "checkbox saggio"),
            (False, True, True): (["Molecole"], "checkbox saggio e reagente"),
        }

        # Ottieni la tupla corrispondente al caso attivo
        key = (molecola, saggio, reagente)
        choices, log_message = cases.get(key, ([], None))

        if visualizza_log_message:
            print(log_message)

        ui.update_checkbox_group("ricerca_output_checkbox", choices=choices)
        ui.update_action_button("ricerca_bottone", disabled=(not choices))


    # Funzione per popolare i select nella navtab "Ricerca"
    @reactive.effect
    def _():
        def update_select_from_query(query_fn, select_id):
            data = query_fn()
            choices = {item[0]: item[1] for item in data}
            ui.update_select(select_id, choices=choices)
        
        update_select_from_query(query.molecole, "select_molecola")
        update_select_from_query(query.saggi, "select_saggio")
        update_select_from_query(query.reagenti, "select_reagente")

    @reactive.effect
    @reactive.event(input.ricerca_bottone)
    def _():
        molecola = input.select_molecola() if input.checkbox_molecola() else None
        saggio = input.select_saggio() if input.checkbox_saggio() else None
        reagente = input.select_reagente() if input.checkbox_reagente() else None

        risultato = query.ricerca_complessa(molecola, saggio, reagente)
        
        @render.ui
        def risultato_ricerca():
            # Converto i df in tabelle HTML
            html1 = risultato['saggi'].to_html(classes="display", table_id="tab1", index=False)
            html2 = risultato['reagenti'].to_html(classes="display", table_id="tab2", index=False)

            # Codice JS per attivare DataTable su entrambe le tabelle
            js = """
            <script>
            $(document).ready(function() {
                $('#tab1').DataTable();
                $('#tab2').DataTable();
            });
            </script>
            """

            # Combino tutto in un unico blocco HTML + JS
            full_html = f"{html1}<br><br>{html2}{js}"

            return ui.HTML(full_html)


    @reactive.effect
    async def send_data():
        data = query.esegui_query_molecole()
        
        await session.send_custom_message("d3data", data)

    # Funzione per salvare la tipologia di molecola nel DB
    @reactive.effect
    @reactive.event(input.salva_tipologia)
    def salva_tipologia():
        try:
            result = query.nuova_tipologia(input.tipologia_id, input.molecole_tip())
        except Exception as e:
            ui.notification_show(f"Errore durante il salvataggio: {e}", type="error")
        else:
            ui.notification_show(result.get("message", "Operazione completata"), type= result.get("status", "info"))


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
        messaggi = []

        for saggio in val.get():
            id_saggio = saggio[1]
            reagenti = query.reagenti_da_saggio(id_saggio)
            lista_reagenti = reagenti['Reagente'].tolist()
            
            if lista_reagenti:
                reagenti_str = ", ".join(lista_reagenti)
                messaggi.append(f"Il saggio {saggio[2]} richiede: {reagenti_str}")
            else:
                messaggi.append(f"Il saggio {saggio[2]} non richiede reagenti.")
        
        # Unisci i messacci con <br> per la separazione
        html_message = "<br>".join(messaggi)

        return ui.HTML(html_message)

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

        if id_saggio == "" or not id_reagenti:
            ui.notification_show("Compila entrambi i campi", type="error")
            return
        
        success_msgs = []
        error_msgs = []

        # IMPORTANTE !!!!!!!!!!!!!!!!!!!!!
        # MODIFICARE MESSAGE PER DIRE QUALI MOLECOLE HANNO DATO ERRORE
        # NON NECESSARIO IN CASO DI SUCCESS
        for id_reagente in id_reagenti:
            result = query.saggi_reagenti(id_saggio, id_reagente)
            if result.get("status") == "success":
                success_msgs.append(result.get("message", "Operazione riuscita"))
            else:
                error_msgs.append(result.get("message", "Errore sconosciuto"))

        # Mostra i messaggi
        if success_msgs:
            ui.notification_show("\n".join(success_msgs), type="message")
        if error_msgs:
            ui.notification_show("\n".join(error_msgs), type="error")

    @render.data_frame
    def associazioni_df():
        df = query.associazioni()
        
        return render.DataTable(df)
    

app = App(app_ui, server)