from dotenv import load_dotenv
# load_dotenv SIEMPRE va primero para que todas las variables del .env esten disponibles en todo el proyecto
load_dotenv()

from os import getenv
from app import create_app

# APP_ENV sirve para indicar en que entorno arrancara el proyecto (development | production)
# En local no es necesario definirla, en Render se define como production
app = create_app(getenv('APP_ENV', 'development'))

if __name__ == '__main__':
    app.run()
