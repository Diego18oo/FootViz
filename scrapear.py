import requests
import http.client
import gzip
import json
import ScraperFC as sfc
from flask import Flask, render_template, request, jsonify
from pprint import pprint
from io import BytesIO
import requests

# Parchear requests para registrar todas las llamadas
original_get = requests.get

def custom_get(*args, **kwargs):
    print(f"Solicitud GET a: {args[0]}")
    return original_get(*args, **kwargs)

requests.get = custom_get

fbref = sfc.FBref()

def sacar_tabla(liga):
    print(f"Obteniendo tabla para: {liga}")
    tabla_base = fbref.scrape_league_table(year='2024-2025', league=liga)
    print(f"Tabla obtenida para {liga}: {len(tabla_base[0])} equipos")

    tabla = tabla_base[0][['Rk','Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'Pts']]
    tabla_formateada = [
        {
            "rk": row["Rk"],
            "club": row["Squad"],
            "pj": row["MP"],
            "v": row["W"],
            "e": row["D"],
            "d": row["L"],
            "ga": row["GF"],
            "gc": row["GA"],
            "pts": row["Pts"]
        }
        for _, row in tabla.iterrows()
    ]
    return tabla_formateada


if __name__ == "__main__":
    print ("\nVer Ligas \n")
    liga = input("\nIngresa una liga:")
    tabla_formateada = sacar_tabla(liga)
    print("\n")
    pprint(tabla_formateada)

