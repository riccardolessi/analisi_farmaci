from shiny import ui, render, reactive, module
import pandas as pd

@module.ui
def cerca_reagenti_ui():
    return(
    ui.input_select("molecole_reagenti", "Seleziona la molecola", choices = []),
    ui.input_action_button("cerca_saggi", "Cerca saggi"),
    ui.output_data_frame("saggi_reag"),
    ui.input_action_button("cerca_reagenti_mol", "Cerca reagenti per i saggi", disabled = True),
    ui.card(
        ui.output_ui("reagenti_mol"),
    )
    )
@module.server
def cerca_reagenti_server(input, output, session, query):
    val = reactive.Value()

    @reactive.effect
    def molecole_reagenti():
        molecole = query.molecole()
        mol = {mol[0]: mol[1] for mol in molecole}
        ui.update_select("molecole_reagenti", choices = mol)

    @render.data_frame
    @reactive.event(input.cerca_saggi)
    def saggi_reag():
        saggi = query.saggi(input.molecole_reagenti())
        val.set(saggi)
        df = pd.DataFrame(saggi, columns=['id esito', 'id saggio', 'saggio'])
        ui.update_action_button("cerca_reagenti_mol", disabled = False)
        return df
    
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
