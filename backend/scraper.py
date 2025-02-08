import ScraperFC as sfc
from pprint import pprint
from models import Equipos
from config import db
from config import app  # Importa el objeto app para obtener el contexto


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
            "pts": row["Pts"],
            "liga": liga  # Agregamos la liga directamente

        }
        for _, row in tabla.iterrows()
    ]
    
    return tabla_formateada


if __name__ == "__main__":
    print ("\nVer Ligas \n")
    with app.app_context():
        liga = input("\nIngresa una liga:")
        tabla_formateada = sacar_tabla(liga)
        print("\n")
        pprint(tabla_formateada)
