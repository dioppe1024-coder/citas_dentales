# API Consultorio Dental 🦷

API REST para la gestión de citas de un consultorio dental.
Hecha con **Flask + Flask-RESTful + SQLAlchemy (ORM) + PostgreSQL + Pydantic + JWT**.

## Entidades

| Tabla | Descripción |
|---|---|
| `usuarios` | Personal del consultorio que inicia sesión (UUID, password con bcrypt) |
| `pacientes` | Datos del paciente (DNI único, soft delete) |
| `odontologos` | Datos del odontólogo (COP único, especialidad, soft delete) |
| `citas` | Fecha, hora, motivo, estado (`PROGRAMADA`, `ATENDIDA`, `CANCELADA`), FK a paciente y odontólogo |

Relaciones: un **paciente** tiene muchas **citas** y un **odontólogo** tiene muchas **citas** (1 - n).

## Endpoints

| Método | Ruta | Protegida | Descripción |
|---|---|---|---|
| GET | `/estado` | No | Estado del servidor y de la BD |
| POST | `/registro` | No | Registrar usuario |
| POST | `/login` | No | Devuelve la JWT |
| GET | `/perfil` | Sí | Datos del usuario logueado |
| GET / POST | `/pacientes` | Sí | Listar (`?page`, `?perPage`, `?buscar`) / crear |
| GET / PUT / DELETE | `/paciente/<id>` | Sí | Ver (con historial de citas) / actualizar / eliminar |
| GET / POST | `/odontologos` | Sí | Listar (`?especialidad`) / crear |
| GET / PUT / DELETE | `/odontologo/<id>` | Sí | Ver / actualizar / eliminar |
| GET / POST | `/citas` | Sí | Listar (`?fecha`, `?odontologoId`, `?pacienteId`, `?estado`, paginado) / crear |
| GET / PUT / DELETE | `/cita/<id>` | Sí | Ver / reprogramar o cambiar estado / cancelar |

Las rutas protegidas requieren el header `Authorization: Bearer <token>`.

### Reglas de negocio de las citas
- Solo se pueden programar en fecha/hora futura (zona horaria de Lima).
- Horario de atención: 08:00 a 20:00.
- Un odontólogo no puede tener dos citas programadas a la misma hora (el paciente tampoco).
- Las citas `ATENDIDA` o `CANCELADA` ya no se pueden modificar.
- `DELETE /cita/<id>` no borra la cita, la **cancela**.
- No se puede eliminar un paciente u odontólogo con citas programadas.

---

