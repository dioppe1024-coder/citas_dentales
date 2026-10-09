from pydantic import BaseModel, Field, ConfigDict, PositiveInt, field_validator
from datetime import date, time
from app.models import EstadoCita
from .pacientes import PacienteResumenSchema
from .odontologos import OdontologoResumenSchema

# Horario de atencion del consultorio
HORA_APERTURA = time(8, 0)
HORA_CIERRE = time(20, 0)


class CitaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None)
    fecha: date = Field(examples=['2026-10-20'])
    hora: time = Field(examples=['09:30'])
    motivo: str = Field(min_length=1, examples=['Limpieza dental'])
    observaciones: str | None = Field(default=None)
    # Si no se envia el estado, la cita se crea como PROGRAMADA
    estado: EstadoCita = Field(default=EstadoCita.PROGRAMADA)
    pacienteId: PositiveInt
    odontologoId: PositiveInt

    @field_validator('hora')
    def validar_horario(cls, valor):
        if valor < HORA_APERTURA or valor >= HORA_CIERRE:
            raise ValueError('La hora debe estar dentro del horario de atencion (08:00 a 20:00)')
        # Se quitan segundos y microsegundos para que 09:30:15 y 09:30 sean la misma hora
        return valor.replace(second=0, microsecond=0)


# Lo que se devuelve al cliente: la cita con la informacion de su paciente y odontologo
# Gracias a los relationship, pydantic puede leer cita.paciente y cita.odontologo directamente
class CitaDetalleSchema(CitaSchema):
    paciente: PacienteResumenSchema
    odontologo: OdontologoResumenSchema
