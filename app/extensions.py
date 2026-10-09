from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# ORM para la comunicacion con la base de datos
db = SQLAlchemy()

# Administrador de migraciones de la bd
migrate = Migrate()

# Administrador de las JWT (autenticacion)
jwt = JWTManager()
