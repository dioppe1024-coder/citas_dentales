from app.extensions import db
from sqlalchemy import Column, types


class Odontologo(db.Model):
    __tablename__ = 'odontologos'

    id = Column(type_=types.Integer, autoincrement=True, primary_key=True)
    nombre = Column(type_=types.Text, nullable=False)
    apellidos = Column(type_=types.Text, nullable=False)
    # Codigo de colegiatura (Colegio Odontologico del Peru)
    cop = Column(type_=types.VARCHAR(10), unique=True, nullable=False)
    especialidad = Column(type_=types.Text, default='Odontologia general')
    telefono = Column(type_=types.VARCHAR(15))
    eliminado = Column(type_=types.Boolean, default=False, nullable=False)
