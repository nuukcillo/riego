import pandas as pd
import pygal
import os
from pygal.style import Style
import random
from database.riego_repository import load_data
# dibuja un grafico de barras con los valores datos
def plot_barchar_riego(xvalues, yvalues, partida=""):
    # colores de los graficos
    colores = ['#563f46', '#80ced6', '#618685', '#36486b']

    #estilo del gráfico
    estilo = Style(background='transparent',

                   value_colors=('white',),
                   #escoger un color aleatorio para las barras
                   colors=[colores[random.randint(0, 3)]] * len(xvalues),
                   value_font_family='googlefont:Raleway',
                   title_font_size=50,
                   label_font_size=30,
                   major_label_font_size=30,
                   tooltip_font_size=30,
                   font_family='googlefont:Raleway')

    bar_chart = pygal.Bar(title="{}".format(partida.iloc[0, 1]), margin_right=50, x_label_rotation=20,
                          show_legend=False, style=estilo,  print_values=True, print_zeroes=False)

    bar_chart.x_labels = xvalues
    bar_chart.add("Litros", yvalues)

    bar_chart.render_to_file('static/images/{}.svg'.format(partida.iloc[0, 0]))


def plot_riego_semanal():
    # Load data from database
    counters, parcelas = load_data()

    # Create a dictionary to store the total liters per parcel
    total_liters = {parcela: 0 for parcela in counters['partida'].tolist()}

    # Calculate total liters for each parcel
    for parcela in total_liters.keys():
        csv_file = os.path.join('csv_files', f"{parcela}.csv")
        if not os.path.exists(csv_file):
            continue

        litros = pd.read_csv(csv_file)
        litros['Total'] = litros['Total'].apply(lambda x: x.split(' ')[0])
        litros['Total'] = pd.to_numeric(litros['Total'], errors='coerce').fillna(0)
        total_liters[parcela] = litros['Total'].sum()

    # Create a bar chart
    bar_chart = pygal.Bar()
    bar_chart.title = 'Total Liters of Water Used Per Parcel This Week'

    for parcela, total in total_liters.items():
        nombre_parcela = parcelas[parcelas['filename'].str.contains(parcela)]
        if not nombre_parcela.empty:
            bar_chart.add(nombre_parcela.iloc[0, 1], total)

    # Save the chart to a file
    bar_chart.render_to_file('riego_semanal.svg')

if __name__ == "__main__":
    plot_riego_semanal()
