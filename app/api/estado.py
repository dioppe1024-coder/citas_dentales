from flask_restful import Resource
from sqlalchemy import text
from app.extensions import db


# Endpoint publico para verificar que el servidor y la base de datos estan vivos (util en produccion)
class EstadoController(Resource):
    def get(self):
        try:
            db.session.execute(text('SELECT 1'))
            baseDatos = 'conectada'
        except Exception:
            baseDatos = 'sin conexion'

        return {
            'message': 'API Consultorio Dental funcionando',
            'baseDatos': baseDatos
        }
