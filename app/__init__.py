from flask import Flask
from flask_restful import Api
from .config import config_map
from .extensions import db, migrate, jwt
from .models import *
from .api import (EstadoController, RegistroController, LoginController, PerfilController,
                  PacientesController, PacienteController, OdontologosController, OdontologoController,
                  CitasController, CitaController)


def create_app(env='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[env])

    # Flask-RESTful intercepta los errores y los convierte en 500, con esta propiedad dejamos que
    # flask-jwt-extended responda sus propios errores (401 cuando no se manda la JWT o es invalida)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError('Falta la variable de entorno DATABASE_URL')
    if not app.config.get('JWT_SECRET_KEY'):
        raise RuntimeError('Falta la variable de entorno JWT_SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    registrarErroresJwt()

    api = Api(app)

    # Rutas publicas
    api.add_resource(EstadoController, '/', '/estado')
    api.add_resource(RegistroController, '/registro')
    api.add_resource(LoginController, '/login')

    # Rutas protegidas (requieren JWT en el header Authorization: Bearer <token>)
    api.add_resource(PerfilController, '/perfil')
    api.add_resource(PacientesController, '/pacientes')
    api.add_resource(PacienteController, '/paciente/<int:id>')
    api.add_resource(OdontologosController, '/odontologos')
    api.add_resource(OdontologoController, '/odontologo/<int:id>')
    api.add_resource(CitasController, '/citas')
    api.add_resource(CitaController, '/cita/<int:id>')

    return app


def registrarErroresJwt():
    # Personalizamos los mensajes de error de la JWT para que esten en español y con el mismo formato de la API
    @jwt.unauthorized_loader
    def sinToken(motivo):
        return {'message': 'Se requiere la JWT (Authorization: Bearer <token>)'}, 401

    @jwt.invalid_token_loader
    def tokenInvalido(motivo):
        return {'message': 'JWT invalida'}, 401

    @jwt.expired_token_loader
    def tokenExpirado(header, payload):
        return {'message': 'La JWT ha expirado, vuelva a iniciar sesion'}, 401
