import pandas as pd
import pygal
from webscrapU import get_dataframe_filtered_by_user
from pygal.style import Style

# dibuja un grafico de barras con los valores datos
def plot_barchar_riego(xvalues, yvalues, partida=""):
    # fuente
    estilo = Style(background='transparent',

                   value_colors=('white',),

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


def dibujar(usuario):
    # leer y filtrar parcelas por usuario
    parcelas = pd.read_csv("contadores.tsv", sep="\t", header=None, names=['user', 'partida', 'contador'])
    parcelas_usuario = get_dataframe_filtered_by_user(parcelas, usuario)

    # leer csv para escribir el nombre bueno de la parcela en el grafico
    datos_parcelas = pd.read_csv("datos_parcelas.tsv", delimiter="\t")

    lista_parcelas = parcelas_usuario['partida'].tolist()

    # dibujar los graficos de las parcelas del usuario dado
    for parcela in lista_parcelas:
        nombrecsv = "{}.csv".format(parcela)
        litros = pd.read_csv(nombrecsv)
        litros = litros.drop(['L. inicial', 'L. final'], axis=1)

        litros['Total'] = litros['Total'].apply(lambda x: x.split(' ')[0])
        litros['Total'] = pd.to_numeric(litros['Total'], errors='coerce').fillna(0)
        litros['Fin'] = pd.to_datetime(litros.Fin).dt.date
        litros['Inicio'] = pd.to_datetime(litros.Fin).dt.date
        # litros['Semana'] = litros['Inicio'].apply(check_if_current_week)

        litros_ultima_semana = litros.tail(7)

        datos_parcelas = pd.read_csv("datos_parcelas.tsv", delimiter="\t")

        plot_barchar_riego(litros_ultima_semana['Inicio'].apply(lambda x: x.strftime('%d/%b')),
                           litros_ultima_semana['Total'],
                           datos_parcelas[datos_parcelas['filename'].str.contains(nombrecsv.split('.')[0])])

    return lista_parcelas
