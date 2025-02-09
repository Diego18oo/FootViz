import os
import httpx
import time
# Variable global para la última actualización (en segundos)
last_update = 0
CACHE_TIMEOUT = 15 * 60  # 15 minutos

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("GITHUB_TOKEN no está configurado")  # Esto debería aparecer en los logs si no se encuentra el token
else:
    print("GITHUB_TOKEN encontrado (httpx)")  # Confirmación (no imprimas el valor real)

    # Parche para httpx.get
    original_httpx_get = httpx.get
    def token_httpx_get(url, **kwargs):
        headers = kwargs.get("headers", {})
        # Agregar la cabecera Authorization si no existe
        if "Authorization" not in headers:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        kwargs["headers"] = headers
        return original_httpx_get(url, **kwargs)

    httpx.get = token_httpx_get

    # Parche para httpx.stream
    original_httpx_stream = httpx.stream

    def token_httpx_stream(*args, **kwargs):
        headers = kwargs.get("headers", {})
        if "Authorization" not in headers:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        kwargs["headers"] = headers
        return original_httpx_stream(*args, **kwargs)

    httpx.stream = token_httpx_stream

from flask import jsonify, render_template, request, make_response
from config import app, db
from models import Equipos
from scraper import sacar_tabla
import requests

#export HOME=/c/Users/amrr1

@app.route('/health', methods=["GET"])
def health():
    return "OK", 200

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
    global last_update
     # Si la solicitud es HEAD, no queremos ejecutar scraping (solo devolvemos 200 OK)
    if request.method == "HEAD":
        return make_response("", 200)
    liga = request.args.get('liga', 'EPL')
    
    # Si han pasado menos de 15 minutos desde la última actualización, no volver a hacer scraping
    if time.time() - last_update > CACHE_TIMEOUT:
        try:
            # Borrar registros antiguos para la liga
            Equipos.query.filter_by(liga=liga).delete()
            db.session.commit()
            
            # Ejecutar el scraping
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
                    liga=liga
                )
                db.session.add(nuevo_equipo)
            db.session.commit()
            last_update = time.time()
        except Exception as e:
            # Podrías registrar el error y/o devolver una respuesta con error
            return f"Error en scraping: {e}", 500
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
    app.run(debug=False)
