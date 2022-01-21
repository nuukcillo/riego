from flask import Flask, render_template
import time
import pandas as pd
from flask.views import MethodView
from flask_simplelogin import SimpleLogin, login_required

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
    usuarios = pd.read_csv("userpass.tsv", sep="\t", header=None, names=['user', 'psswd', 'name'])
    nombre_usuarios = usuarios['name'].tolist()
    id_usuarios = usuarios['user'].tolist()
    return render_template('index.html', users_name=nombre_usuarios, users_len=len(nombre_usuarios),
                           users_id=id_usuarios)


@app.route('/gente/<people>')
@login_required
def gente(people):
    parcelas_ret = plotpygal.dibujar(people)

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
                                                                        index_names=False, index=False, justify='center'
                                                                        ))


if __name__ == "__main__":
    app.run()
