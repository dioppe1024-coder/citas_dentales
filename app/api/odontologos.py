from flask_restful import Resource, request
from pydantic import ValidationError, TypeAdapter
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Odontologo, Cita, EstadoCita
from app.schemas import OdontologoSchema


class OdontologosController(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        # Opcional: ?especialidad=ortodoncia
        especialidad = request.args.get('especialidad')

        consulta = db.session.query(Odontologo).filter(Odontologo.eliminado == False)
        if especialidad:
            consulta = consulta.filter(Odontologo.especialidad.ilike(f'%{especialidad}%'))

        odontologos = consulta.order_by(Odontologo.apellidos).all()

        adaptador = TypeAdapter(list[OdontologoSchema])
        return {
            'content': adaptador.dump_python(adaptador.validate_python(odontologos), mode='json')
        }

    def post(self):
        try:
            dataValidada = OdontologoSchema.model_validate(request.get_json())

            odontologoExistente = db.session.query(Odontologo).with_entities(Odontologo.id).filter(
                Odontologo.cop == dataValidada.cop).first()

            if odontologoExistente:
                return {
                    'message': f'Ya existe un odontologo con el COP {dataValidada.cop}'
                }, 400

            nuevoOdontologo = Odontologo(**dataValidada.model_dump(exclude={'id'}))
            db.session.add(nuevoOdontologo)
            db.session.commit()

            return {
                'message': 'Odontologo creado exitosamente',
                'content': OdontologoSchema.model_validate(nuevoOdontologo).model_dump(mode='json')
            }, 201

        except ValidationError as error:
            return {
                'message': 'Error al crear el odontologo',
                'content': error.errors(include_context=False)
            }, 400


class OdontologoController(Resource):
    method_decorators = [jwt_required()]

    def validarOdontologo(self, id):
        return db.session.query(Odontologo).filter(Odontologo.id == id, Odontologo.eliminado == False).first()

    def get(self, id):
        odontologoEncontrado = self.validarOdontologo(id)
        if not odontologoEncontrado:
            return {
                'message': 'Odontologo no existe'
            }, 404

        respuesta = OdontologoSchema.model_validate(odontologoEncontrado).model_dump(mode='json')
        # Cantidad de citas pendientes del odontologo
        respuesta['citasProgramadas'] = len(
            [cita for cita in odontologoEncontrado.citas if cita.estado == EstadoCita.PROGRAMADA])

        return {
            'content': respuesta
        }

    def put(self, id):
        odontologoEncontrado = self.validarOdontologo(id)
        if not odontologoEncontrado:
            return {
                'message': 'Odontologo no existe'
            }, 404

        try:
            dataValidada = OdontologoSchema.model_validate(request.get_json())

            copRepetido = db.session.query(Odontologo).with_entities(Odontologo.id).filter(
                Odontologo.cop == dataValidada.cop, Odontologo.id != id).first()

            if copRepetido:
                return {
                    'message': f'Ya existe otro odontologo con el COP {dataValidada.cop}'
                }, 400

            for llave, valor in dataValidada.model_dump(exclude={'id'}).items():
                setattr(odontologoEncontrado, llave, valor)

            db.session.commit()

            return {
                'message': 'Odontologo actualizado exitosamente',
                'content': OdontologoSchema.model_validate(odontologoEncontrado).model_dump(mode='json')
            }

        except ValidationError as error:
            return {
                'message': 'Error al actualizar el odontologo',
                'content': error.errors(include_context=False)
            }, 400

    def delete(self, id):
        odontologoEncontrado = self.validarOdontologo(id)
        if not odontologoEncontrado:
            return {
                'message': 'Odontologo no existe'
            }, 404

        citasPendientes = db.session.query(Cita).filter(
            Cita.odontologoId == id, Cita.estado == EstadoCita.PROGRAMADA).count()

        if citasPendientes > 0:
            return {
                'message': f'El odontologo tiene {citasPendientes} cita(s) programada(s), reasignelas o cancelelas antes de eliminarlo'
            }, 400

        odontologoEncontrado.eliminado = True
        db.session.commit()

        return {
            'message': 'Odontologo eliminado exitosamente'
        }
