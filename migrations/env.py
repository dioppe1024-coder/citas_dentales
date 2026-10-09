import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# Objeto de configuración de Alembic. Da acceso a todo lo que está en alembic.ini
config = context.config

# Activamos los logs usando el archivo de configuración (alembic.ini).
# Esto nos permite ver en consola qué está haciendo Alembic en cada momento.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # Para versiones anteriores de Flask-SQLAlchemy (menor a 3)
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Para Flask-SQLAlchemy 3 en adelante
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    # Obtenemos la URL de conexión a la base de datos.
    # El %% es necesario porque Alembic usa % como carácter especial en su config.
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Le decimos a Alembic cuál es la URL de la base de datos (la saca de Flask)
# y también le pasamos los metadatos de nuestros modelos para que pueda
# detectar automáticamente los cambios cuando hacemos "flask db migrate"
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db


def get_metadata():
    # Retorna los metadatos de la base de datos (estructura de tablas y columnas).
    # En proyectos con múltiples bases de datos hay varios metadatos; aquí solo hay uno.
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """
    Ejecuta las migraciones en modo 'offline' (sin conexión activa a la BD).

    En este modo Alembic solo genera el SQL que se debería ejecutar,
    sin conectarse realmente. Útil para revisar qué cambios se harían
    antes de aplicarlos, o cuando no tienes acceso directo a la base de datos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Ejecuta las migraciones en modo 'online' (con conexión activa a la BD).

    Este es el modo normal cuando corremos "flask db upgrade".
    Alembic se conecta a la base de datos y aplica los cambios directamente.
    """

    def process_revision_directives(context, revision, directives):
        # Si hacemos "flask db migrate" y no hay cambios en los modelos,
        # Alembic no genera un archivo de migración vacío. Simplemente avisa
        # que no detectó cambios. Evita tener archivos de migración inútiles.
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No se detectaron cambios en el esquema.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


# Punto de entrada: dependiendo del modo en que corre Alembic,
# ejecuta las migraciones online u offline
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()