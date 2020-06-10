from flask import Flask, render_template
import time
import pandas as pd
import plotpygal

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def home():

    usuarios = pd.read_csv("userpass.tsv", sep="\t", header=None, names=['user', 'psswd', 'name'])
    nombre_usuarios = usuarios['name'].tolist()
    id_usuarios = usuarios['user'].tolist()
    return render_template('index.html', users_name=nombre_usuarios, users_len=len(nombre_usuarios), users_id=id_usuarios)


@app.route('/gente/<people>')
def gente(people):
    parcelas_ret = plotpygal.dibujar(people)

    return render_template('bar.html', parcelas=parcelas_ret, num_parcelas=len(parcelas_ret), cache=str(time.time()))


# @app.route("/bar")
# def bar():
#     plotpygal.main()
#     img_url = 'static/images/c_villar.svg?cache=' + str(time.time())
#     return render_template('bar.html', image_url=img_url)
#

if __name__ == "__main__":
    app.run()
