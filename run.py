from dotenv import load_dotenv

# load_dotenv lee el archivo .env y carga todas las variables de entorno.
# Tiene que ir primero que todo lo demás para que cuando importemos
# la app ya encuentre las variables listas (como la URL de la base de datos).
load_dotenv()

from os import getenv
from app import create_app

# APP_ENV le dice a la app en qué modo debe arrancar.
# Si no existe la variable (como en nuestra máquina local), usa 'development' por defecto.
# En Render definimos APP_ENV=production para que use la configuración de producción.
app = create_app(getenv('APP_ENV', 'development'))

# Este bloque solo corre cuando ejecutamos "python run.py" directamente.
# En producción Gunicorn importa la variable 'app' sin pasar por aquí.
if __name__ == '__main__':
    app.run()