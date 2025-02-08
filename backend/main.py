import os
import requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("GITHUB_TOKEN no está configurado")  # Esto debería aparecer en los logs si no se encuentra el token
else:
    print("GITHUB_TOKEN encontrado")  # Confirmación (no imprimas el valor real)

# ... Código del parche ...
if GITHUB_TOKEN:
    original_get = requests.get

    def token_get(*args, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        kwargs["headers"] = headers
        return original_get(*args, **kwargs)

    requests.get = token_get

    # Parcheo de requests.Session.get
    original_session_get = requests.Session.get

    def token_session_get(self, *args, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        kwargs["headers"] = headers
        return original_session_get(self, *args, **kwargs)

    requests.Session.get = token_session_get

    # Parcheo de requests.request
    original_request = requests.request

    def token_request(method, url, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        kwargs["headers"] = headers
        return original_request(method, url, **kwargs)

    requests.request = token_request

# Ahora, parcheamos urllib3.PoolManager.urlopen para cubrir llamadas a nivel inferior
import urllib3
original_urlopen = urllib3.PoolManager.urlopen

def token_urlopen(self, method, url, body=None, headers=None, **kwargs):
    if headers is None:
        headers = {}
    if "Authorization" not in headers and GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    print(f"Making {method} request to {url} with headers: {headers}")  # solo para debug

    return original_urlopen(self, method, url, body=body, headers=headers, **kwargs)

urllib3.PoolManager.urlopen = token_urlopen

from flask import jsonify, render_template, request
from config import app, db
from models import Equipos
from scraper import sacar_tabla
import requests

#export HOME=/c/Users/amrr1

@app.route('/test-sofascore')
def test_sofascore():
    try:
        response = requests.get("https://www.sofascore.com")
        return f"Status Code: {response.status_code}", response.status_code
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/<string:liga>', methods=["GET"])
def tabla_liga(liga):
    # Si necesitas mapear el valor de la URL a un nombre "real" (por ejemplo, 'laliga' → 'La Liga')
    league_names = {
        'epl': 'EPL',
        'laliga': 'La Liga',
        'ligue1': 'Ligue 1',
        'seriea': 'Serie A',
        'bundesliga': 'Bundesliga'
    }
    # Normalizamos la entrada
    liga_seleccionada = league_names.get(liga.lower(), 'EPL')
    
    # 1. Eliminar registros anteriores para esa liga
    Equipos.query.filter_by(liga=liga_seleccionada).delete()
    db.session.commit()
    
    # 2. Obtener datos nuevos y agregarlos a la BD
    nuevos_datos = sacar_tabla(liga_seleccionada)
    for equipo in nuevos_datos:
        nuevo_equipo = Equipos(
            posicion=equipo["rk"],
            nombre=equipo["club"],
            partidos_jugados=equipo["pj"],
            victorias=equipo["v"],
            empates=equipo["e"],
            derrotas=equipo["d"],
            goles_anotados=equipo["ga"],
            goles_concedidos=equipo["gc"],
            puntos=equipo["pts"],
            liga=liga_seleccionada
        )
        db.session.add(nuevo_equipo)
    db.session.commit()
    
    # 3. Consultar y ordenar los registros para esa liga
    tabla = Equipos.query.filter_by(liga=liga_seleccionada).order_by(Equipos.posicion).all()
    return render_template('index.html', tabla=tabla, liga=liga_seleccionada)


@app.route('/', methods=["GET"])
def index():
    liga = 'EPL'  # Obtiene la liga del parámetro de la URL
    if liga:
        # 1. Eliminar registros anteriores para esa liga
        Equipos.query.filter_by(liga=liga).delete()
        db.session.commit()
        # 2. Obtener datos nuevos y agregarlos a la BD
        nuevos_datos = sacar_tabla(liga)
        for equipo in nuevos_datos:
            nuevo_equipo = Equipos(
                posicion=equipo["rk"],
                nombre=equipo["club"],
                partidos_jugados=equipo["pj"],
                victorias=equipo["v"],
                empates=equipo["e"],
                derrotas=equipo["d"],
                goles_anotados=equipo["ga"],
                goles_concedidos=equipo["gc"],
                puntos=equipo["pts"],
                liga=liga  # Asignar la liga
            )
            db.session.add(nuevo_equipo)
        db.session.commit()  # Confirmar inserción
    # 3. Consultar solo los registros de la liga 'EPL'
    tabla = Equipos.query.filter_by(liga=liga).order_by(Equipos.posicion).all()
    return render_template('index.html', tabla=tabla, liga=liga)

    #json_tabla = list(map(lambda x:x.to_json(), tabla)) 
    #return jsonify({"tabla": json_tabla})

"""
@app.route('/laliga', methods=["GET"])
def tabla_laliga():
    liga = 'La Liga'  # Obtiene la liga del parámetro de la URL
    if liga:
        # 1. Eliminar registros anteriores para esa liga
        Equipos.query.filter_by(liga=liga).delete()
        db.session.commit()
        # 2. Obtener datos nuevos y agregarlos a la BD
        nuevos_datos = sacar_tabla(liga)
        for equipo in nuevos_datos:
            nuevo_equipo = Equipos(
                posicion=equipo["rk"],
                nombre=equipo["club"],
                partidos_jugados=equipo["pj"],
                victorias=equipo["v"],
                empates=equipo["e"],
                derrotas=equipo["d"],
                goles_anotados=equipo["ga"],
                goles_concedidos=equipo["gc"],
                puntos=equipo["pts"],
                liga=liga  # Asignar la liga
            )
            db.session.add(nuevo_equipo)
        db.session.commit()  # Confirmar inserción
    # 3. Consultar solo los registros de la liga 'La Liga'
    tabla = Equipos.query.filter_by(liga=liga).order_by(Equipos.posicion).all()
    json_tabla = list(map(lambda x:x.to_json(), tabla)) 
    return jsonify({"tabla": json_tabla})

@app.route('/seriea', methods=["GET"])
def tabla_seriea():
    liga = 'Serie A'  # Obtiene la liga del parámetro de la URL
    if liga:
        # 1. Eliminar registros anteriores para esa liga
        Equipos.query.filter_by(liga=liga).delete()
        db.session.commit()
        # 2. Obtener datos nuevos y agregarlos a la BD
        nuevos_datos = sacar_tabla(liga)
        for equipo in nuevos_datos:
            nuevo_equipo = Equipos(
                posicion=equipo["rk"],
                nombre=equipo["club"],
                partidos_jugados=equipo["pj"],
                victorias=equipo["v"],
                empates=equipo["e"],
                derrotas=equipo["d"],
                goles_anotados=equipo["ga"],
                goles_concedidos=equipo["gc"],
                puntos=equipo["pts"],
                liga=liga  # Asignar la liga
            )
            db.session.add(nuevo_equipo)
        db.session.commit()  # Confirmar inserción
    # 3. Consultar solo los registros de la liga 'Serie A'
    tabla = Equipos.query.filter_by(liga=liga).order_by(Equipos.posicion).all()
    json_tabla = list(map(lambda x:x.to_json(), tabla)) 
    return jsonify({"tabla": json_tabla})

@app.route('/ligue1', methods=["GET"])
def tabla_ligue1():
    liga = 'Ligue 1'  # Obtiene la liga del parámetro de la URL
    if liga:
        # 1. Eliminar registros anteriores para esa liga
        Equipos.query.filter_by(liga=liga).delete()
        db.session.commit()
        # 2. Obtener datos nuevos y agregarlos a la BD
        nuevos_datos = sacar_tabla(liga)
        for equipo in nuevos_datos:
            nuevo_equipo = Equipos(
                posicion=equipo["rk"],
                nombre=equipo["club"],
                partidos_jugados=equipo["pj"],
                victorias=equipo["v"],
                empates=equipo["e"],
                derrotas=equipo["d"],
                goles_anotados=equipo["ga"],
                goles_concedidos=equipo["gc"],
                puntos=equipo["pts"],
                liga=liga  # Asignar la liga
            )
            db.session.add(nuevo_equipo)
        db.session.commit()  # Confirmar inserción
    # 3. Consultar solo los registros de la liga 'Ligue 1'
    tabla = Equipos.query.filter_by(liga=liga).order_by(Equipos.posicion).all()
    json_tabla = list(map(lambda x:x.to_json(), tabla)) 
    return jsonify({"tabla": json_tabla})

@app.route('/bundesliga', methods=["GET"])
def tabla_bundes():
    liga = 'Bundesliga'  # Obtiene la liga del parámetro de la URL
    if liga:
        # 1. Eliminar registros anteriores para esa liga
        Equipos.query.filter_by(liga=liga).delete()
        db.session.commit()
        # 2. Obtener datos nuevos y agregarlos a la BD
        nuevos_datos = sacar_tabla(liga)
        for equipo in nuevos_datos:
            nuevo_equipo = Equipos(
                posicion=equipo["rk"],
                nombre=equipo["club"],
                partidos_jugados=equipo["pj"],
                victorias=equipo["v"],
                empates=equipo["e"],
                derrotas=equipo["d"],
                goles_anotados=equipo["ga"],
                goles_concedidos=equipo["gc"],
                puntos=equipo["pts"],
                liga=liga  # Asignar la liga
            )
            db.session.add(nuevo_equipo)
        db.session.commit()  # Confirmar inserción
    # 3. Consultar solo los registros de la liga 'EPL'
    tabla = Equipos.query.filter_by(liga=liga).order_by(Equipos.posicion).all()
    json_tabla = list(map(lambda x:x.to_json(), tabla)) 
    return jsonify({"tabla": json_tabla})
"""
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
