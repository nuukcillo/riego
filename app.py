from flask import Flask, render_template
import time
from flask_simplelogin import SimpleLogin, login_required

from database.riego_repository import load_data, obtener_inicial
import plotpygal
import riegosemanal

from config import Config

app = Flask(__name__)

app.config.from_object(Config)
SimpleLogin(app)


@app.route("/")
@app.route("/index")
@login_required
def home():
    _, usuarios = load_data()

    nombre_usuarios = usuarios['name'].tolist()
    id_usuarios = usuarios['user'].tolist()
    print(nombre_usuarios, id_usuarios)
    return render_template('index.html', users_name=nombre_usuarios, users_len=len(nombre_usuarios),
                           users_id=id_usuarios)


@app.route('/gente/<people>')
@login_required
def gente(people):
    parcelas_ret = []  # Lista que guardará los nombres de los archivos SVG de cada parcela

    # Obtener las parcelas relacionadas con el usuario
    counters, _ = load_data()
    inicial = obtener_inicial(people)
    df = riegosemanal.obtener_valores_riego(counters, inicial=inicial, todos=True).iloc[:, -7:]

    # Dibujar gráficos para cada parcela
    for parcela in df.index:
        # Filtrar los datos para cada parcela
        parcela_data = df.loc[parcela]
        
        # Generar el gráfico para la parcela
        plotpygal.plot_barchar_riego(parcela_data.index.tolist(), parcela_data.tolist(), parcela)

        # Añadir el nombre del archivo SVG generado a la lista
        parcelas_ret.append(f"{parcela}.svg")

    # Pasar los nombres de los archivos SVG y el número de parcelas a la plantilla
    return render_template('bar.html', parcelas=parcelas_ret, num_parcelas=len(parcelas_ret), cache=str(time.time()))



# @app.route("/bar")
# def bar():
#     plotpygal.main()
#     img_url = 'static/images/c_villar.svg?cache=' + str(time.time())
#     return render_template('bar.html', image_url=img_url)
#

@app.route('/riegosemanal')
@login_required
def riego():
    litros_semanales = riegosemanal.obtener_datos()
    return render_template('riego.html', tabla=litros_semanales.to_html(classes="responsible-table striped",
                                                                        index_names=False, index=True, justify='center'
                                                                        ))


if __name__ == "__main__":
    app.run()
