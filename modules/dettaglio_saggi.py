from shiny import ui, render, reactive, module
from pathlib import Path

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
            ui.br(),
            ui.output_text("molecola_trattata"),
        ),
    )

@module.server
def dettaglio_saggi_server(input, output, session, query):

    # Funzione per popolare il select con i saggi esistenti
    @reactive.effect
    def select_saggi_esistenti():
        # Popola il select con i saggi esistenti
        saggi = query.saggi_new()
        choices = {saggio[0]: saggio[1] for saggio in saggi}
        ui.update_select("select_saggi_esistenti", choices=choices)

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
                if saggio_details['schema_saggio_img']:
                    img = str(Path(__file__).parent.parent / "assets" / "img_saggi" / saggio_details['schema_saggio_img'])
                else:
                    img = str(Path(__file__).parent.parent / "assets" / "img_saggi" / "immagine_non_disponibile.png")
    
                return {
                    "src": img,
                    "height": "400px",
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
