from config import db

class Equipos(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    posicion = db.Column(db.Integer, nullable = False)
    nombre = db.Column(db.String(20), nullable = False)
    partidos_jugados = db.Column(db.Integer, nullable = False)
    victorias = db.Column(db.Integer, nullable = False)
    empates = db.Column(db.Integer, nullable = False)
    derrotas = db.Column(db.Integer, nullable = False)
    goles_anotados = db.Column(db.Integer, nullable = False)
    goles_concedidos = db.Column(db.Integer, nullable = False)
    puntos = db.Column(db.Integer, nullable = False)
    liga = db.Column(db.String(50), nullable=False)  # Campo para identificar la liga

    __table_args__ = (
        db.UniqueConstraint('liga', 'posicion', name='unique_liga_posicion'),
        db.UniqueConstraint('liga', 'nombre', name='unique_liga_nombre'),
    )


    def to_json(self):
        return {
            "id": self.id,
            "posicion": self.posicion,
            "nombre": self.nombre,
            "partidosJugados": self.partidos_jugados,
            "victorias": self.victorias,
            "empates": self.empates,
            "derrotas": self.derrotas,
            "golesAnotados": self.goles_anotados,
            "golesConcedidos": self.goles_concedidos,
            "puntos": self.puntos,
            "liga": self.liga

        }