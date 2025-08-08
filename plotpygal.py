from datetime import datetime
import pygal
from pygal.style import Style
import random

# Función para generar el gráfico de barras
def plot_barchar_riego(xvalues, yvalues, partida):
    # Colores de los gráficos
    colores = ["#5c4249", '#80ced6', '#618685', '#36486b']

    # Estilo del gráfico
    estilo = Style(background='transparent',
                   value_colors=('white',),
                   colors=[colores[random.randint(0, 3)]] * len(xvalues),
                   value_font_family='googlefont:Raleway',
                   title_font_size=50,
                   label_font_size=30,
                   major_label_font_size=30,
                   tooltip_font_size=30,
                   font_family='googlefont:Raleway')
    
    xvalues_formateados = [datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m') for date in xvalues]

    # Crear el gráfico de barras
    bar_chart = pygal.Bar(title=partida, margin_right=50, x_label_rotation=20,
                          show_legend=False, style=estilo, print_values=True, print_zeroes=False)

    # Asignar las etiquetas y los valores de las barras
    bar_chart.x_labels = xvalues_formateados
    bar_chart.add("Litros", yvalues)

    # Renderizar el gráfico en un archivo SVG
    bar_chart.render_to_file(f'static/images/{partida}.svg')
