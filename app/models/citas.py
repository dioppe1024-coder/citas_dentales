from app.extensions import db
from sqlalchemy import Column, types, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum


# Enumerador con los posibles estados de una cita
class EstadoCita(Enum):
    PROGRAMADA = 'PROGRAMADA'
    ATENDIDA = 'ATENDIDA'
    CANCELADA = 'CANCELADA'


class Cita(db.Model):
    __tablename__ = 'citas'

    id = Column(type_=types.Integer, autoincrement=True, primary_key=True)
    fecha = Column(type_=types.Date, nullable=False)
    hora = Column(type_=types.Time, nullable=False)
    motivo = Column(type_=types.Text, nullable=False)
    observaciones = Column(type_=types.Text)
    estado = Column(type_=types.Enum(EstadoCita), nullable=False, default=EstadoCita.PROGRAMADA)
    pacienteId = Column(ForeignKey('pacientes.id'), type_=types.Integer, nullable=False, name='paciente_id')
    odontologoId = Column(ForeignKey('odontologos.id'), type_=types.Integer, nullable=False, name='odontologo_id')

    # cita.paciente > instancia del Paciente | paciente.citas > lista de citas del paciente
    paciente = relationship('Paciente', backref='citas')
    # cita.odontologo > instancia del Odontologo | odontologo.citas > lista de citas del odontologo
    odontologo = relationship('Odontologo', backref='citas')
