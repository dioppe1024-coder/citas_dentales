from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date


class PacienteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # El id no se envia al crear, solo se devuelve
    id: int | None = Field(default=None)
    nombre: str = Field(min_length=1, examples=['Maria'])
    apellidos: str = Field(min_length=1, examples=['Lopez Quispe'])
    # pattern > expresion regular, el DNI debe tener exactamente 8 digitos
    dni: str = Field(pattern=r'^\d{8}$', examples=['45678912'])
    telefono: str | None = Field(default=None, pattern=r'^\+?\d{7,15}$', examples=['987654321'])
    correo: EmailStr | None = Field(default=None)
    fechaNacimiento: date | None = Field(default=None, examples=['1990-05-21'])


# Version corta del paciente que se muestra dentro de una cita
class PacienteResumenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellidos: str
    dni: str
    telefono: str | None
