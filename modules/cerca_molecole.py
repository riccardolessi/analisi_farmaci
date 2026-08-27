from shiny import ui, render, module, reactive

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _notifica_errore(messaggio: str) -> None:
    ui.notification_show(messaggio, type="error")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@module.ui
def cerca_molecole_ui():
    return (
        ui.h3("Ricerca esito saggio"),
        ui.p(
            "Seleziona una molecola e il relativo saggio per visualizzarne l'esito.",
            class_="text-muted"
        ),
        ui.hr(),
        ui.h5("1. Seleziona la molecola"),
        ui.input_select("molecole", None, choices=[]),
        ui.h5("2. Seleziona il saggio"),
        ui.p("I saggi disponibili si aggiornano automaticamente in base alla molecola selezionata.", class_="text-muted"),
        ui.input_select("saggi", None, choices=[]),
        ui.hr(),
        ui.input_action_button("cerca", "Visualizza esito", icon=ui.tags.i(class_="fa fa-search")),
        ui.br(),
        ui.br(),
        ui.output_text("esito_saggio"),
    )


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

@module.server
def cerca_molecole_server(input, output, session, query):

    # -- Sync select -------------------------------------------------------

    @reactive.effect
    def _sync_molecole():
        try:
            molecole = query.molecole()
            ui.update_select("molecole", choices={m[0]: m[1] for m in molecole})
        except Exception as e:
            print(f"Errore caricamento molecole: {e}")
            _notifica_errore("Errore nel caricamento delle molecole.")

    @reactive.effect
    @reactive.event(input.molecole)
    def _sync_saggi():
        molecola_id = input.molecole()
        if not molecola_id:
            ui.update_select("saggi", choices={})
            return
        try:
            saggi = query.saggi(molecola_id)
            ui.update_select("saggi", choices={s[1]: s[2] for s in saggi})
        except Exception as e:
            print(f"Errore caricamento saggi: {e}")
            _notifica_errore("Errore nel caricamento dei saggi.")

    # -- Render ------------------------------------------------------------

    @render.text
    @reactive.event(input.cerca)
    def esito_saggio():
        molecola_id = input.molecole()
        saggio_id = input.saggi()

        if not molecola_id or not saggio_id:
            return "Seleziona una molecola e un saggio prima di procedere."

        try:
            esito = query.esito(molecola_id, saggio_id)

            if not esito or len(esito) <= 3:
                return "Nessun esito disponibile: il saggio non risulta effettuato."

            return f"Esito: {esito[3].capitalize()}"

        except Exception as e:
            print(f"Errore recupero esito: {e}")
            return f"Errore durante la ricerca. Riprovare o contattare il supporto."



# from shiny import ui, render, module, reactive

# @module.ui
# def cerca_molecole_ui():
#     """UI del modulo 'Cerca Molecole'."""
#     return (
#         ui.h4("Cerca esito saggio per molecola"),
#         ui.input_select("molecole", "Seleziona la molecola", choices=[]),
#         ui.input_select("saggi", "Seleziona il saggio", choices=[]),
#         ui.input_action_button("cerca", "Cerca"),
#         ui.br(),
#         ui.output_text("esito_saggio"),
#     )


# @module.server
# def cerca_molecole_server(input, output, session, query):
#     """Server del modulo 'Cerca Molecole'."""

#     # --- 1️⃣ Popola la select delle molecole ---
#     @reactive.effect
#     def aggiorna_molecole():
#         """Popola la lista delle molecole al caricamento."""
#         try:
#             molecole = query.molecole()  # Restituisce [(id, nome), ...]
#             scelte = {mol[0]: mol[1] for mol in molecole}
#             ui.update_select("molecole", choices=scelte)
#         except Exception as e:
#             print(f"Errore durante il caricamento delle molecole: {e}")
#             ui.notification_show("Errore nel caricamento delle molecole.", type="error")

#     # --- 2️⃣ Aggiorna i saggi in base alla molecola selezionata ---
#     @reactive.effect
#     @reactive.event(input.molecole)
#     def aggiorna_saggi():
#         """Aggiorna la lista dei saggi in base alla molecola selezionata."""
#         try:
#             molecola_id = input.molecole()
#             if not molecola_id:
#                 ui.update_select("saggi", choices={})
#                 return
            
#             saggi = query.saggi(molecola_id)
#             scelte = {s[1]: s[2] for s in saggi}
#             ui.update_select("saggi", choices=scelte)
#         except Exception as e:
#             print(f"Errore durante il caricamento dei saggi: {e}")
#             ui.notification_show("Errore nel caricamento dei saggi.", type="error")

#     # --- 3️⃣ Mostra l’esito del saggio ---
#     @render.text
#     @reactive.event(input.cerca)
#     def esito_saggio():
#         """Mostra l'esito del saggio selezionato."""
#         try:
#             molecola_id = input.molecole()
#             saggio_id = input.saggi()

#             if not molecola_id or not saggio_id:
#                 return "⚠️ Seleziona una molecola e un saggio prima di cercare."

#             esito = query.esito(molecola_id, saggio_id)

#             if not esito or len(esito) <= 3:
#                 return "Saggio non fatto"

#             return f"✅ Esito: {esito[3].capitalize()}"
        
#         except Exception as e:
#             print(f"Errore durante il recupero dell’esito: {e}")
#             return f"❌ Errore durante la ricerca: {e}"
