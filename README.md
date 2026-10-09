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

## Correr en local

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac / Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la base de datos en PostgreSQL (pgAdmin o psql)
#    CREATE DATABASE consultorio_dental;

# 4. Copiar .env.example a .env y completar DATABASE_URL y JWT_SECRET_KEY

# 5. Ejecutar las migraciones (crea las tablas)
flask db upgrade

# 6. Levantar el servidor
python run.py
```

> La carpeta `migrations/` ya incluye la migración inicial. Si modificas algún modelo:
> `flask db migrate -m "descripcion del cambio"` y luego `flask db upgrade`.

## Probar con Bruno

1. Abrir Bruno → **Open Collection** → seleccionar la carpeta `bruno/`.
2. Elegir el entorno **Local** (o **Produccion**).
3. Ejecutar **Registro** y luego **Login**: el token se guarda solo en la variable `{{token}}`.
4. Ya puedes usar el resto de requests. Orden sugerido: crear paciente → crear odontólogo → crear cita.

---

## Despliegue en producción (Render)

### 1. Subir el proyecto a GitHub
El `.gitignore` ya excluye `.env` y `venv`, **nunca subas el `.env`**.

### 2. Crear la base de datos
**Opción A: Render Postgres:** New → Postgres → plan Free. Copiar la **Internal Database URL**.
> ⚠️ La base de datos gratuita de Render expira a los 30 días.

**Opción B: Neon (neon.tech):** crear un proyecto gratis y copiar la connection string. No expira.

### 3. Crear el Web Service
New → Web Service → conectar el repositorio de GitHub.

| Campo | Valor |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `flask db upgrade && gunicorn run:app` |
| Instance Type | Free |

### 4. Variables de entorno (pestaña *Environment*)

| Variable | Valor |
|---|---|
| `DATABASE_URL` | la URL de la base de datos del paso 2 |
| `JWT_SECRET_KEY` | un texto largo y aleatorio |
| `APP_ENV` | `production` |
| `FLASK_APP` | `run.py` |

### 5. Deploy
Al terminar, Render te da una URL tipo `https://consultorio-dental-xxxx.onrender.com`.
Abre `https://.../estado` y debe responder `"baseDatos": "conectada"`.
Luego en Bruno cambia el `baseUrl` del entorno **Produccion** por esa URL.

> En el plan Free el servicio se "duerme" tras 15 min sin uso; la primera petición puede tardar ~1 minuto.
