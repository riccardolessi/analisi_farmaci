from shiny import ui, module
from pathlib import Path

script_file =  Path(__file__).parent.parent / "script.js"

@module.ui
def grafico_torta_ui():
    return (
        ui.tags.head(
            ui.tags.script(src="https://d3js.org/d3.v7.min.js"),
        ),
        ui.h2("Grafico Sunburst con D3.js"),
        ui.tags.div(id="chart-container"),
        ui.include_js(script_file),
    )