from config import app, db

with app.app_context():
    # Opcional: Imprimir la ubicación actual del archivo de la base de datos
    print("Usando base de datos:", app.config["SQLALCHEMY_DATABASE_URI"])
    
    db.drop_all()
    db.create_all()
    print("La base de datos se ha actualizado.")
