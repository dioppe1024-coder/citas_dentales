from flask_restful import Resource, request
from pydantic import ValidationError
from bcrypt import gensalt, hashpw, checkpw
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Usuario
from app.schemas import RegistroUsuarioSchema, LoginUsuarioSchema, UsuarioSchema


class RegistroController(Resource):
    def post(self):
        try:
            dataValidada = RegistroUsuarioSchema.model_validate(request.get_json())

            # SELECT id FROM usuarios WHERE correo = '...' LIMIT 1;
            usuarioExistente = db.session.query(Usuario).with_entities(Usuario.id).filter(
                Usuario.correo == dataValidada.correo).first()

            if usuarioExistente:
                return {
                    'message': 'Usuario ya existe'
                }, 400

            # Hashing de la password en un solo paso
            passwordHasheada = hashpw(dataValidada.password.encode(), gensalt()).decode()

            nuevoUsuario = Usuario(
                **dataValidada.model_dump(exclude={'password'}),
                password=passwordHasheada
            )

            db.session.add(nuevoUsuario)
            db.session.commit()

            return {
                'message': 'Usuario registrado exitosamente'
            }, 201

        except ValidationError as error:
            return {
                'message': 'Error al registrar el usuario',
                'content': error.errors(include_context=False)
            }, 400


class LoginController(Resource):
    def post(self):
        try:
            dataValidada = LoginUsuarioSchema.model_validate(request.get_json())

            usuarioEncontrado = db.session.query(Usuario).filter(
                Usuario.correo == dataValidada.correo).first()

            # Por seguridad se devuelve el mismo mensaje si el correo no existe o si la password es incorrecta
            if not usuarioEncontrado or not checkpw(dataValidada.password.encode(), usuarioEncontrado.password.encode()):
                return {
                    'message': 'Credenciales incorrectas'
                }, 401

            # identity DEBE ser un string, por eso convertimos el UUID con str()
            jwt = create_access_token(identity=str(usuarioEncontrado.id))

            return {
                'message': 'Login exitoso',
                'content': jwt
            }

        except ValidationError as error:
            return {
                'message': 'Error al hacer el login',
                'content': error.errors(include_context=False)
            }, 400


class PerfilController(Resource):
    # La JWT es OBLIGATORIA para acceder a este metodo
    @jwt_required()
    def get(self):
        id = get_jwt_identity()

        usuarioEncontrado = db.session.query(Usuario).filter(Usuario.id == id).first()

        if not usuarioEncontrado:
            return {
                'message': 'Usuario no existe'
            }, 404

        return {
            'content': UsuarioSchema.model_validate(usuarioEncontrado).model_dump(mode='json')
        }
