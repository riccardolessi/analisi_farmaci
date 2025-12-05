from shiny import ui, render, reactive, module
from pathlib import Path
import sqlite3

# Percorsi base per le risorse statiche
ASSETS_DIR = Path(__file__).parent.parent / "assets" / "img_saggi"
IMMAGINE_NON_DISPONIBILE = str(ASSETS_DIR / "immagine_non_disponibile.png")

@module.ui
def dettaglio_saggi_ui():
    return (
        ui.input_select("select_saggi_esistenti", "Saggi esistenti", choices=[]),
        ui.input_action_button("visualizza_saggio", "Visualizza"),
        ui.card(
            ui.output_text("saggio_details_nome_saggio"),
            ui.output_image("saggio_details_schema_saggio_img"),
            ui.br(),
            ui.output_ui("saggio_details_descrizione_saggio"),
            ui.br(),
            ui.output_text("reagenti_saggio"),
            # ui.br(),
            # ui.output_text("molecola_trattata"),
        ),
    )

@module.server
def dettaglio_saggi_server(input, output, session, query):

    # Variabili reattive per memorizzare i dettagli del saggio
    nome_saggio = reactive.Value("")
    dettagli_saggio = reactive.Value("")
    dettaglio_reagenti = reactive.Value("")

    @render.text
    def saggio_details_nome_saggio():
        return nome_saggio.get()
    
    @render.ui
    def saggio_details_descrizione_saggio():
        return ui.HTML(dettagli_saggio.get().replace("\n", "<br>"))
    
    @render.text
    def reagenti_saggio():
        return dettaglio_reagenti.get()

    # Funzione per popolare il select con i saggi esistenti
    @reactive.effect
    def select_saggi_esistenti():
        # Popola il select con i saggi esistenti
        saggi = cerca_saggi()
        choices = {saggio[0]: saggio[1] for saggio in saggi}
        ui.update_select("select_saggi_esistenti", choices=choices)

    # Logica per visualizzare i dettagli del saggio selezionato
    @reactive.effect
    @reactive.event(input.visualizza_saggio)
    def visualizza_saggio():
        saggio_id = input.select_saggi_esistenti()

        # Controllo se un saggio è stato selezionato
        if not saggio_id:
            ui.notification_show("Seleziona un saggio esistente", type="error")
            return
        
        try:
            # Recupera i dettagli del saggio dal database
            saggio_details = query.get_saggio_details(saggio_id)

            # Controlla se il saggio esiste
            if not saggio_details:
                ui.notification_show("Saggio non trovato", type="error")
                return
            
            # Aggiorna le variabili reattive con i dettagli del saggio
            nome_saggio.set(saggio_details['nome_saggio'])
            dettagli_saggio.set(saggio_details['descrizione'])
            
            reagenti = query.get_reagenti_saggio_new(saggio_id)
            if not reagenti:
                dettaglio_reagenti.set("Nessun reagente associato a questo saggio.")
            else:
                reagenti = "Reagenti associati: " + ", ".join(reagenti)
                dettaglio_reagenti.set(reagenti)
            
            @render.image
            def saggio_details_schema_saggio_img():
                if saggio_details['schema_saggio_img']:
                    img = str(Path(__file__).parent.parent / "assets" / "img_saggi" / saggio_details['schema_saggio_img'])
                else:
                    img = str(Path(__file__).parent.parent / "assets" / "img_saggi" / "immagine_non_disponibile.png")
    
                return {
                    "src": img,
                    "height": "400px",
                }

        except Exception as e:
            ui.notification_show(f"Errore durante il recupero del saggio: {e}", type="error")

def cerca_saggi(db_path='analisi_farmaci.db'):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        query = "SELECT id, nome_saggio FROM saggi_new WHERE visualizza_dettaglio = 1"
        cursor.execute(query)
        
        saggi = cursor.fetchall()
        
    return saggi