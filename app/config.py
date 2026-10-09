from os import getenv
from datetime import timedelta


def obtener_database_url():
    # Render (y otros proveedores) entregan la cadena como postgres://... o postgresql://...
    # SQLAlchemy necesita saber que driver usar, en este caso psycopg (version 3) > postgresql+psycopg://...
    url = getenv('DATABASE_URL', '')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


class Base:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = obtener_database_url()
    # Llave con la que se firmaran las JWT, NUNCA se debe subir al repositorio
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    # Duracion de validez de la JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)


class Development(Base):
    DEBUG = True


class Production(Base):
    DEBUG = False


config_map = {
    'development': Development,
    'production': Production
}
