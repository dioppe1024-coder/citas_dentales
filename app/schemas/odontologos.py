from pydantic import BaseModel, Field, ConfigDict


class OdontologoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None)
    nombre: str = Field(min_length=1, examples=['Carlos'])
    apellidos: str = Field(min_length=1, examples=['Ramirez Torres'])
    cop: str = Field(min_length=3, max_length=10, examples=['COP12345'])
    especialidad: str = Field(default='Odontologia general', min_length=1, examples=['Ortodoncia'])
    telefono: str | None = Field(default=None, pattern=r'^\+?\d{7,15}$')


class OdontologoResumenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellidos: str
    especialidad: str | None
