from shiny import App, reactive, render, ui
import query
from modules.cerca_molecole import *
from modules.cerca_saggi import *
from modules.cerca_reagenti import *
from modules.grafico_torta import *
from modules.dettaglio_saggi import *
from modules.riconoscimento_sottostrutture import *
from modules.predizione_ml import *


app_ui = ui.page_navbar(
    ui.nav_panel(
        "Cerca molecole",
        cerca_molecole_ui("cerca_molecole")
    ),
    ui.nav_panel(
        "Cerca saggi",
        cerca_saggi_ui("cerca_saggi_ui")
    ),
    ui.nav_panel(
        "Cerca reagenti",
        cerca_reagenti_ui("cerca_reagenti_ui")
    ),
    ui.nav_panel(
        "Grafico a torta",
        grafico_torta_ui("grafico_torta")
    ),
    ui.nav_panel(
        "Dettaglio saggi",
        ui.page_navbar(
            ui.nav_panel(
                "Saggi esistenti",
                dettaglio_saggi_ui("dettaglio_saggi")
            )
        )
    ),
    ui.nav_panel(
        "Riconoscimento sottostrutture",
        riconoscimento_sottostrutture_ui("riconoscimento_sottostrutture")
    ),
    ui.nav_panel(
        "Predizione saggio con Acqua di Bromo",
        predizione_ml_ui("predizione_ml")
    ),
    title="App Analisi dei Medicinali"
)

def server(input, output, session):
    
    cerca_molecole_server("cerca_molecole", query=query)

    cerca_saggi_server("cerca_saggi_ui", query=query)

    cerca_reagenti_server("cerca_reagenti_ui", query=query)

    dettaglio_saggi_server("dettaglio_saggi", query=query)

    riconoscimento_sottostrutture_server("riconoscimento_sottostrutture")

    predizione_ml_server("predizione_ml")

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
            with open("modello.pkl", "rb") as f:
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