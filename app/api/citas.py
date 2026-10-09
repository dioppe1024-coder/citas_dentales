from flask_restful import Resource, request
from pydantic import ValidationError, TypeAdapter
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from zoneinfo import ZoneInfo
from app.extensions import db
from app.models import Cita, EstadoCita, Paciente, Odontologo
from app.schemas import CitaSchema, CitaDetalleSchema
from app.util import paginationInfo, obtenerPaginacion

# El servidor en produccion suele estar en hora UTC, por eso usamos la zona horaria de Lima
ZONA_HORARIA = ZoneInfo('America/Lima')


def validarReglasCita(data, citaId=None):
    
    #Valida las reglas de negocio de una cita. Retorna un mensaje de error o None si todo esta bien.
    #citaId se usa al actualizar para no compararse consigo misma.
    
    paciente = db.session.query(Paciente).with_entities(Paciente.id).filter(
        Paciente.id == data.pacienteId, Paciente.eliminado == False).first()
    if not paciente:
        return f'El paciente {data.pacienteId} no existe'

    odontologo = db.session.query(Odontologo).with_entities(Odontologo.id).filter(
        Odontologo.id == data.odontologoId, Odontologo.eliminado == False).first()
    if not odontologo:
        return f'El odontologo {data.odontologoId} no existe'

    # Las validaciones de horario solo aplican a las citas que siguen programadas
    if data.estado != EstadoCita.PROGRAMADA:
        return None

    # datetime.combine une la fecha y la hora en un solo datetime
    fechaHoraCita = datetime.combine(data.fecha, data.hora, tzinfo=ZONA_HORARIA)
    if fechaHoraCita < datetime.now(ZONA_HORARIA):
        return 'No se puede programar una cita en una fecha u hora pasada'

    # Un odontologo no puede tener dos citas programadas a la misma hora
    consultaOdontologo = db.session.query(Cita).with_entities(Cita.id).filter(
        Cita.odontologoId == data.odontologoId,
        Cita.fecha == data.fecha,
        Cita.hora == data.hora,
        Cita.estado == EstadoCita.PROGRAMADA)
    if citaId:
        consultaOdontologo = consultaOdontologo.filter(Cita.id != citaId)
    if consultaOdontologo.first():
        return 'El odontologo ya tiene una cita programada en esa fecha y hora'

    # Un paciente tampoco puede tener dos citas a la misma hora
    consultaPaciente = db.session.query(Cita).with_entities(Cita.id).filter(
        Cita.pacienteId == data.pacienteId,
        Cita.fecha == data.fecha,
        Cita.hora == data.hora,
        Cita.estado == EstadoCita.PROGRAMADA)
    if citaId:
        consultaPaciente = consultaPaciente.filter(Cita.id != citaId)
    if consultaPaciente.first():
        return 'El paciente ya tiene una cita programada en esa fecha y hora'

    return None


class CitasController(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        # Query params opcionales: ?fecha=2026-10-20&odontologoId=1&pacienteId=2&estado=PROGRAMADA&page=1&perPage=10
        pagina, porPagina = obtenerPaginacion(request.args)
        consulta = db.session.query(Cita)

        fecha = request.args.get('fecha')
        if fecha:
            try:
                # strptime convierte un string a fecha usando el patron indicado
                consulta = consulta.filter(Cita.fecha == datetime.strptime(fecha, '%Y-%m-%d').date())
            except ValueError:
                return {
                    'message': 'La fecha debe tener el formato YYYY-MM-DD'
                }, 400

        odontologoId = request.args.get('odontologoId', type=int)
        if odontologoId:
            consulta = consulta.filter(Cita.odontologoId == odontologoId)

        pacienteId = request.args.get('pacienteId', type=int)
        if pacienteId:
            consulta = consulta.filter(Cita.pacienteId == pacienteId)

        estado = request.args.get('estado')
        if estado:
            if estado.upper() not in EstadoCita.__members__:
                return {
                    'message': f'Estado invalido, los valores permitidos son: {", ".join(EstadoCita.__members__)}'
                }, 400
            consulta = consulta.filter(Cita.estado == EstadoCita[estado.upper()])

        total = consulta.count()
        citas = consulta.order_by(Cita.fecha, Cita.hora).offset((pagina - 1) * porPagina).limit(porPagina).all()

        adaptador = TypeAdapter(list[CitaDetalleSchema])
        return {
            'content': adaptador.dump_python(adaptador.validate_python(citas), mode='json'),
            'pageInfo': paginationInfo(total, pagina, porPagina)
        }

    def post(self):
        try:
            dataValidada = CitaSchema.model_validate(request.get_json())

            # Una cita nueva siempre nace como PROGRAMADA
            dataValidada.estado = EstadoCita.PROGRAMADA

            error = validarReglasCita(dataValidada)
            if error:
                return {
                    'message': error
                }, 400

            nuevaCita = Cita(**dataValidada.model_dump(exclude={'id'}))
            db.session.add(nuevaCita)
            db.session.commit()

            return {
                'message': 'Cita programada exitosamente',
                'content': CitaDetalleSchema.model_validate(nuevaCita).model_dump(mode='json')
            }, 201

        except ValidationError as error:
            return {
                'message': 'Error al crear la cita',
                'content': error.errors(include_context=False)
            }, 400


class CitaController(Resource):
    method_decorators = [jwt_required()]

    def validarCita(self, id):
        return db.session.query(Cita).filter(Cita.id == id).first()

    def get(self, id):
        citaEncontrada = self.validarCita(id)
        if not citaEncontrada:
            return {
                'message': 'Cita no existe'
            }, 404

        return {
            'content': CitaDetalleSchema.model_validate(citaEncontrada).model_dump(mode='json')
        }

    def put(self, id):
        # Sirve para reprogramar (cambiar fecha/hora/odontologo) o cambiar el estado (ATENDIDA, CANCELADA)
        citaEncontrada = self.validarCita(id)
        if not citaEncontrada:
            return {
                'message': 'Cita no existe'
            }, 404

        if citaEncontrada.estado != EstadoCita.PROGRAMADA:
            return {
                'message': f'La cita ya se encuentra {citaEncontrada.estado.value} y no puede modificarse'
            }, 400

        try:
            dataValidada = CitaSchema.model_validate(request.get_json())

            error = validarReglasCita(dataValidada, citaId=id)
            if error:
                return {
                    'message': error
                }, 400

            for llave, valor in dataValidada.model_dump(exclude={'id'}).items():
                setattr(citaEncontrada, llave, valor)

            db.session.commit()

            return {
                'message': 'Cita actualizada exitosamente',
                'content': CitaDetalleSchema.model_validate(citaEncontrada).model_dump(mode='json')
            }

        except ValidationError as error:
            return {
                'message': 'Error al actualizar la cita',
                'content': error.errors(include_context=False)
            }, 400

    def delete(self, id):
        # No se elimina la cita de la bd, se CANCELA para conservar el historial
        citaEncontrada = self.validarCita(id)
        if not citaEncontrada:
            return {
                'message': 'Cita no existe'
            }, 404

        if citaEncontrada.estado != EstadoCita.PROGRAMADA:
            return {
                'message': f'La cita ya se encuentra {citaEncontrada.estado.value}'
            }, 400

        citaEncontrada.estado = EstadoCita.CANCELADA
        db.session.commit()

        return {
            'message': 'Cita cancelada exitosamente'
        }
