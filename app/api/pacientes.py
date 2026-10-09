from flask_restful import Resource, request
from pydantic import ValidationError, TypeAdapter
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from app.extensions import db
from app.models import Paciente, Cita, EstadoCita
from app.schemas import PacienteSchema, CitaSchema
from app.util import paginationInfo, obtenerPaginacion


class PacientesController(Resource):
    # Al colocar method_decorators TODOS los metodos de esta clase exigiran la JWT
    method_decorators = [jwt_required()]

    def get(self):
        # Query params: ?page=1&perPage=10&buscar=lopez
        pagina, porPagina = obtenerPaginacion(request.args)
        buscar = request.args.get('buscar')

        consulta = db.session.query(Paciente).filter(Paciente.eliminado == False)

        if buscar:
            # ilike > busqueda sin importar mayusculas o minusculas, el % indica "cualquier texto"
            consulta = consulta.filter(or_(
                Paciente.nombre.ilike(f'%{buscar}%'),
                Paciente.apellidos.ilike(f'%{buscar}%'),
                Paciente.dni.ilike(f'%{buscar}%')
            ))

        # Mismos filtros para el total y para los registros
        total = consulta.count()
        pacientes = consulta.order_by(Paciente.apellidos, Paciente.nombre).offset(
            (pagina - 1) * porPagina).limit(porPagina).all()

        adaptador = TypeAdapter(list[PacienteSchema])
        resultado = adaptador.validate_python(pacientes)

        return {
            'content': adaptador.dump_python(resultado, mode='json'),
            'pageInfo': paginationInfo(total, pagina, porPagina)
        }

    def post(self):
        try:
            dataValidada = PacienteSchema.model_validate(request.get_json())

            pacienteExistente = db.session.query(Paciente).with_entities(Paciente.id).filter(
                Paciente.dni == dataValidada.dni).first()

            if pacienteExistente:
                return {
                    'message': f'Ya existe un paciente con el DNI {dataValidada.dni}'
                }, 400

            nuevoPaciente = Paciente(**dataValidada.model_dump(exclude={'id'}))
            db.session.add(nuevoPaciente)
            db.session.commit()

            return {
                'message': 'Paciente creado exitosamente',
                'content': PacienteSchema.model_validate(nuevoPaciente).model_dump(mode='json')
            }, 201

        except ValidationError as error:
            return {
                'message': 'Error al crear el paciente',
                'content': error.errors(include_context=False)
            }, 400


class PacienteController(Resource):
    method_decorators = [jwt_required()]

    def validarPaciente(self, id):
        return db.session.query(Paciente).filter(Paciente.id == id, Paciente.eliminado == False).first()

    def get(self, id):
        pacienteEncontrado = self.validarPaciente(id)
        if not pacienteEncontrado:
            return {
                'message': 'Paciente no existe'
            }, 404

        respuesta = PacienteSchema.model_validate(pacienteEncontrado).model_dump(mode='json')

        # Gracias al backref='citas' podemos obtener el historial de citas del paciente
        citasOrdenadas = sorted(pacienteEncontrado.citas, key=lambda cita: (cita.fecha, cita.hora), reverse=True)
        adaptador = TypeAdapter(list[CitaSchema])
        respuesta['citas'] = adaptador.dump_python(adaptador.validate_python(citasOrdenadas), mode='json')

        return {
            'content': respuesta
        }

    def put(self, id):
        pacienteEncontrado = self.validarPaciente(id)
        if not pacienteEncontrado:
            return {
                'message': 'Paciente no existe'
            }, 404

        try:
            dataValidada = PacienteSchema.model_validate(request.get_json())

            # Si cambia el DNI, validar que no lo tenga otro paciente
            dniRepetido = db.session.query(Paciente).with_entities(Paciente.id).filter(
                Paciente.dni == dataValidada.dni, Paciente.id != id).first()

            if dniRepetido:
                return {
                    'message': f'Ya existe otro paciente con el DNI {dataValidada.dni}'
                }, 400

            # Actualizamos cada atributo de la instancia con la data validada
            for llave, valor in dataValidada.model_dump(exclude={'id'}).items():
                setattr(pacienteEncontrado, llave, valor)

            db.session.commit()

            return {
                'message': 'Paciente actualizado exitosamente',
                'content': PacienteSchema.model_validate(pacienteEncontrado).model_dump(mode='json')
            }

        except ValidationError as error:
            return {
                'message': 'Error al actualizar el paciente',
                'content': error.errors(include_context=False)
            }, 400

    def delete(self, id):
        pacienteEncontrado = self.validarPaciente(id)
        if not pacienteEncontrado:
            return {
                'message': 'Paciente no existe'
            }, 404

        citasPendientes = db.session.query(Cita).filter(
            Cita.pacienteId == id, Cita.estado == EstadoCita.PROGRAMADA).count()

        if citasPendientes > 0:
            return {
                'message': f'El paciente tiene {citasPendientes} cita(s) programada(s), cancelelas antes de eliminarlo'
            }, 400

        # Soft delete
        pacienteEncontrado.eliminado = True
        db.session.commit()

        return {
            'message': 'Paciente eliminado exitosamente'
        }
