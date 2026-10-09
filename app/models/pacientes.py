from app.extensions import db
from sqlalchemy import Column, types


class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id = Column(type_=types.Integer, autoincrement=True, primary_key=True)
    nombre = Column(type_=types.Text, nullable=False)
    apellidos = Column(type_=types.Text, nullable=False)
    dni = Column(type_=types.VARCHAR(8), unique=True, nullable=False)
    telefono = Column(type_=types.VARCHAR(15))
    correo = Column(type_=types.Text)
    fechaNacimiento = Column(name='fecha_nacimiento', type_=types.Date)
    # Soft delete, el registro no se borra de la bd para no perder su historial de citas
    eliminado = Column(type_=types.Boolean, default=False, nullable=False)
