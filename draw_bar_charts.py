import pandas as pd
import matplotlib.pyplot as plt
from webscrapU import get_dataframe_filtered_by_user




# dibuja un grafico de barras con los valores datos
def plot_barchar_riego(xvalues, yvalues, partida=""):

    #fuente
    font = {'family': 'serif',
            'color': 'darkred',
            'weight': 'normal',
            'size': 16,
            }

    plt.ylabel("Litros",fontdict=font)
    plt.xlabel("Últimos siete días", fontdict=font)
    plt.title("Riego en la última semana en {}".format(partida), fontdict=font)
    plt.bar(xvalues, yvalues)
    for i, v in enumerate(yvalues):
        if v != 0:
            plt.text(i - 0.1, v + 1.5, str(v))
    plt.show()


def dibujar(usuario):

    #leer y filtrar parcelas por usuario
    parcelas = pd.read_csv("contadores.tsv", sep="\t", header=None, names=['user', 'partida', 'contador'])
    parcelas_usuario = get_dataframe_filtered_by_user(parcelas, usuario)

    #leer csv para escribir el nombre bueno de la parcela en el grafico
    datos_parcelas = pd.read_csv("datos_parcelas.tsv", delimiter="\t")

    lista_parcelas = parcelas_usuario['partida'].tolist()

    #dibujar los graficos de las parcelas del usuario dado
    for parcela in lista_parcelas:
        nombrecsv = "{}.csv".format(parcela.partida)

        litros = pd.read_csv(nombrecsv)
        litros = litros.drop(['L. inicial', 'L. final'], axis=1)

        litros['Total'] = litros['Total'].apply(lambda x: x.split(' ')[0])
        litros['Total'] = pd.to_numeric(litros['Total'], errors='coerce').fillna(0)
        litros['Fin'] = pd.to_datetime(litros.Fin).dt.date
        litros['Inicio'] = pd.to_datetime(litros.Fin).dt.date
        litros['Semana'] = litros['Inicio'].apply(check_if_current_week)

        litros_ultima_semana = litros.tail(7)

        #dibujar svg
        plot_barchar_riego(litros_ultima_semana['Inicio'].apply(lambda x: x.strftime('%d/%b')),
                           litros_ultima_semana['Total'],
                           datos_parcelas[datos_parcelas['filename'].str.contains(nombrecsv.split('.')[0])].iloc[0, 1])

    #devuelve las parcelas dibujadas
    return lista_parcelas