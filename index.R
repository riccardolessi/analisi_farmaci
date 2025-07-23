library(shiny)
library(data.tree)
library(collapsibleTree)

# Crea un semplice albero gerarchico
data <- data.frame(
  Level1 = c("Animali", "Animali", "Animali", "Piante", "Piante", "Piante"),
  Level3 = c("Mammiferi", "Mammiferi", "Uccelli", "Alberi", "Fiori", "Fiori"),
  Level2 = c("Cani", "Gatti", "Passeri", "Querce", "Rose", "Tulipani"),
  stringsAsFactors = FALSE
)

# UI
ui <- fluidPage(
  titlePanel("Grafico ad albero con Shiny"),
  collapsibleTreeOutput("tree")
)



# Server
server <- function(input, output) {
  output$tree <- renderCollapsibleTree({
    collapsibleTree(
      data,
      hierarchy = c("Level1", "Level2", "Level3"),
      root = "Regno Vivente",
      width = "100%", height = "600px"
    )
  })
}

# App
shinyApp(ui = ui, server = server)



