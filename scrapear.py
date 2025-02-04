import requests
import http.client
import gzip
import json
from flask import Flask, render_template, request, jsonify
from pprint import pprint
from io import BytesIO


def sacar_tabla(liga):

    try: 
        host = "www.sofascore.com"
        ligas_urls = {
            "Liga MX": "/api/v1/unique-tournament/11620/season/70096/standings/total",
            "Premier League": "/api/v1/unique-tournament/17/season/61627/standings/total",
            "La Liga": "/api/v1/unique-tournament/8/season/61643/standings/total",
            # Agrega más ligas aquí
        }
        if liga not in ligas_urls:
            print("Liga no encontrada")
            return []
        headers = {
                'authority' : 'www.sofascore.com',
                'accept' : '*/*',
                'accept-encoding' : 'gzip, deflate, br, zstd',
                'accept-language' : 'en-US,en;q=0.9,es;q=0.8',
                'baggage' : 'sentry-environment=production,sentry-release=PY2n8D-QSyB56r3U10j0f,sentry-public_key=d693747a6bb242d9bb9cf7069fb57988,sentry-trace_id=40bbcec44ed3460382a7c597f4d02b88',
                'cache-control' : 'max-age=0',
                'cookie' : '_lr_env_src_ats=false; gcid_first=997f751f-4c20-41ef-9616-1fa1c0217d83; __browsiUID=e632dd46-d3b2-4218-9383-42bb86e119eb; _ga=GA1.1.1714250554.1736801964; __qca=P0-841995455-1736801964550; _lr_geo_location_state=JAL; _lr_geo_location=MX; _lr_retry_request=true; clever-last-tracker-66554=8; __gads=ID=14d1d95abf838e29:T=1736801947:RT=1738524114:S=ALNI_MZsz4s9Ic6knTe_kPUdDlN9DEFifA; __gpi=UID=00000fba76e05784:T=1736801947:RT=1738524114:S=ALNI_MbneU43Gi7R4pKiEpAAfSmfwXyAxw; __eoi=ID=eb58d8618227a795:T=1736801947:RT=1738524114:S=AA-AfjY4lypD8hBOHCNROkZ39b0L; FCNEC=%5B%5B%22AKsRol-QatQfcWKqDwmCld8rE94GKoCUPP5RgoWJGDfQIv5nN4Z-E1vCsndMWZLsGGbxiQYjBGwY5Ds2JwZM1El6oQ2L7HQWgfVnm7arVFyg6qtiHL97xHkWaGzJRH5E83-_-TjQ-6gK43uYFJ92xYtIBwy7ZK4Qeg%3D%3D%22%5D%5D; cto_bundle=I26rKF9mRHZXZ0JibWlTdkFuRExMZnBSSlV0NHglMkJZMjVXcHZHUHpGTVZtY09IamQySXhJdk9vdFNLY21Zc0Zna3EyVzFnWHRhTXFvMkhqcWNwclp6VGlGbWlpM05uTEJieE5ndTYxTExyQVRuUkgwNVg2V2ZBd2liRXRuNkhzR21pYk1UZWs4JTJGOEhONGZpZnFxSmlGSVN6d3JBJTNEJTNE; pmtimesig=[[1738533604123,81061509],[1738533604704,581],[1738534963858,1359154]]; _ga_HNQ9P9MGZR=GS1.1.1738533585.9.1.1738535021.38.0.0',
                'if-none-match' : "ca77df1d70",
                'priority' : 'u=1, i',
                'referer' : 'https://www.sofascore.com/tournament/football/mexico/liga-mx-clausura/11620',
                'sec-ch-ua' : '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                'sec-ch-ua-mobile' : '?0',
                'sec-ch-ua-platform' : '"Windows"',
                'sec-fetch-dest' : 'empty',
                'sec-fetch-mode' : 'cors',
                'sec-fetch-site' : 'same-origin',
                'sentry-trace' : '40bbcec44ed3460382a7c597f4d02b88-b26aca780aeafa87',
                'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                'x-requested-with' : 'a50386'

            }
        conn = http.client.HTTPSConnection(host)
        conn.request("GET", ligas_urls[liga], headers=headers)
        response = conn.getresponse()
        # Leer los datos
        raw_data = response.read()

         # 🔍 IMPRIMIR PARA VER QUÉ ESTÁ DEVOLVIENDO LA API
        print("HTTP STATUS:", response.status)
        print("HEADERS:", response.getheaders())
        print("RAW RESPONSE:", raw_data[:500])  # Muestra solo los primeros 500 bytes

         # Si la API devuelve error, no intentar decodificar
        if response.status != 200:
            return jsonify({"error": f"HTTP {response.status} - Sofascore rechazó la petición"}), response.status

        # Descomprimir si la respuesta está en gzip
        if response.getheader("Content-Encoding") == "gzip":
            raw_data = gzip.decompress(raw_data)

        # Decodificar a texto
        data = raw_data.decode("utf-8")

        # Convertir a JSON (si es necesario)
        json_data = json.loads(data)
        #url = ligas_urls[liga]
        #response = requests.get(url, headers=headers)
        
        posiciones = json_data['standings'][0]['rows']
        tabla = [{"posicion": equipo["position"], 
                "nombre": equipo["team"]["name"],
                "pj": equipo["matches"],
                "v": equipo["wins"],
                "e": equipo["draws"],
                "d": equipo["losses"],
                "df": equipo["scoreDiffFormatted"],
                "pts": equipo["points"]} for equipo in posiciones]
        return tabla
    except Exception as e: 
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print ("\nVer Ligas \n")
    liga = input("\nIngresa una liga:")
    tabla = sacar_tabla(liga)
    print("\n")
    pprint(tabla)

