from flask import Flask, render_template, request
from scrapear import sacar_tabla
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/tabla')
def conseguir_tabla():
    liga = request.args.get('liga')
    tabla = sacar_tabla(liga)
    return render_template(
        "tabla.html",
        tabla=tabla
    )


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
