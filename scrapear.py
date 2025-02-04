import requests
import http.client
import gzip
import json
import ScraperFC as sfc
from flask import Flask, render_template, request, jsonify
from pprint import pprint
from io import BytesIO

fbref = sfc.FBref()

def sacar_tabla(liga):
    tabla_base = fbref.scrape_league_table(year='2024-2025', league=liga)
    tabla = tabla_base[0][['Rk','Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'Pts']]
    return tabla


if __name__ == "__main__":
    print ("\nVer Ligas \n")
    liga = input("\nIngresa una liga:")
    tabla = sacar_tabla(liga)
    print("\n")
    pprint(tabla)

