"""creacion de tablas del consultorio

Revision ID: 45e2118fe6ee
Revises:
Create Date: 2026-10-08 22:34:36.897285

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de esta migración.
# revision: el ID único de este archivo.
# down_revision: el ID de la migración anterior (None porque es la primera).
# Alembic usa estos IDs para saber en qué orden aplicar o revertir los cambios.
revision = '45e2118fe6ee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Esta función se ejecuta cuando corremos "flask db upgrade".
    # Crea todas las tablas del proyecto en la base de datos.
    # El orden importa: primero las tablas independientes y luego
    # las que tienen llaves foráneas (citas depende de pacientes y odontologos).

    op.create_table('odontologos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.Text(), nullable=False),
    sa.Column('apellidos', sa.Text(), nullable=False),
    sa.Column('cop', sa.VARCHAR(length=10), nullable=False),   # Código del Colegio Odontológico del Perú, único por odontólogo
    sa.Column('especialidad', sa.Text(), nullable=True),
    sa.Column('telefono', sa.VARCHAR(length=15), nullable=True),
    sa.Column('eliminado', sa.Boolean(), nullable=False),       # Soft delete: en vez de borrar, marcamos como eliminado
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cop')
    )

    op.create_table('pacientes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.Text(), nullable=False),
    sa.Column('apellidos', sa.Text(), nullable=False),
    sa.Column('dni', sa.VARCHAR(length=8), nullable=False),     # DNI único por paciente
    sa.Column('telefono', sa.VARCHAR(length=15), nullable=True),
    sa.Column('correo', sa.Text(), nullable=True),
    sa.Column('fecha_nacimiento', sa.Date(), nullable=True),
    sa.Column('eliminado', sa.Boolean(), nullable=False),       # Soft delete
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dni')
    )

    op.create_table('usuarios',
    sa.Column('id', sa.UUID(), nullable=False),                 # UUID en vez de entero para mayor seguridad
    sa.Column('nombre', sa.Text(), nullable=False),
    sa.Column('apellido', sa.Text(), nullable=True),
    sa.Column('correo', sa.Text(), nullable=False),             # El correo es el nombre de usuario para iniciar sesión
    sa.Column('password', sa.Text(), nullable=False),           # Se guarda hasheado con bcrypt, nunca en texto plano
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('correo')
    )

    # La tabla citas va al final porque referencia a pacientes y odontologos
    op.create_table('citas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora', sa.Time(), nullable=False),
    sa.Column('motivo', sa.Text(), nullable=False),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('estado', sa.Enum('PROGRAMADA', 'ATENDIDA', 'CANCELADA', name='estadocita'), nullable=False),  # En PostgreSQL el ENUM es un tipo propio
    sa.Column('paciente_id', sa.Integer(), nullable=False),
    sa.Column('odontologo_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['odontologo_id'], ['odontologos.id'], ),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Esta función se ejecuta cuando corremos "flask db downgrade".
    # Deshace todo lo que hizo upgrade(): elimina las tablas en orden inverso
    # para no violar las restricciones de llaves foráneas.

    op.drop_table('citas')      # Primero citas porque depende de las otras dos
    op.drop_table('usuarios')
    op.drop_table('pacientes')
    op.drop_table('odontologos')

    # En PostgreSQL el ENUM 'estadocita' es un tipo de dato independiente
    # que no se elimina automáticamente al borrar la tabla.
    # Lo eliminamos manualmente para no dejar basura en la base de datos.
    sa.Enum(name='estadocita').drop(op.get_bind(), checkfirst=True)