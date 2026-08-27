from shiny import App, reactive, ui
import query

from modules.cerca_molecole import cerca_molecole_ui, cerca_molecole_server
from modules.cerca_saggi import cerca_saggi_ui, cerca_saggi_server
from modules.cerca_reagenti import cerca_reagenti_ui, cerca_reagenti_server
from modules.grafico_torta import grafico_torta_ui
from modules.dettaglio_saggi import dettaglio_saggi_ui, dettaglio_saggi_server
from modules.riconoscimento_sottostrutture import (
    riconoscimento_sottostrutture_ui,
    riconoscimento_sottostrutture_server,
)
from modules.predizione_ml import predizione_ml_ui, predizione_ml_server


app_ui = ui.page_navbar(
    ui.nav_panel(
        "Cerca molecole",
        cerca_molecole_ui("cerca_molecole")
    ),
    ui.nav_panel(
        "Cerca saggi",
        cerca_saggi_ui("cerca_saggi")
    ),
    ui.nav_panel(
        "Cerca reagenti",
        cerca_reagenti_ui("cerca_reagenti")
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

    cerca_saggi_server("cerca_saggi", query=query)

    cerca_reagenti_server("cerca_reagenti", query=query)

    dettaglio_saggi_server("dettaglio_saggi", query=query)

    riconoscimento_sottostrutture_server("riconoscimento_sottostrutture")

    predizione_ml_server("predizione_ml")

    # grafico_torta ha solo la UI: i dati del sunburst vengono passati a
    # script.js con un custom message, che il modulo non può inviare da solo.
    @reactive.effect
    async def invia_dati_sunburst():
        await session.send_custom_message("d3data", query.esegui_query_molecole())


app = App(app_ui, server)
