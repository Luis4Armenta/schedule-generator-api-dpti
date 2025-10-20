from typing import Optional, TypedDict, List
from pydantic import BaseModel, Field
from bson import ObjectId

class Session(TypedDict):
  day: str
  start_time: str
  end_time: str

ScheduleCourse = List[Session]

class CourseAvailability(BaseModel):
  sequence: str
  subject: str
  course_availability: int

class Course(BaseModel):
  _id: Optional[ObjectId] = Field(default_factory=ObjectId, alias='_id')

  plan: str = Field(title="Plan", description="Plan al que pertence el curso")
  level: str = Field(title="Nivel", description="Nivel del curso")
  career: str = Field(title="Carrera", description="Carrera a la que pertenece el curso")
  shift: str = Field(title="Turno", description="Turno en el que se imparte el curso")
  semester: str = Field(title="Semestre", description="Semestre del curso")
  sequence: str = Field(title="Secuencia", description="Grupo al que pertenece el curso")
  teacher: str = Field(title="Instrictor", description="Nombre del instructor que imparte el curso")
  subject: str = Field(title="Asignatura", description="Nombre de la asignatura")
  course_availability: Optional[int] = Field(title="Disponibilidad", description="Número de lugares disponibles", default=40)
  teacher_positive_score: Optional[float] = Field(title="Puntaje positivo del profesor", description="Puntaje positivo promedio del profesor calculado por el sistema.")
  
  required_credits: Optional[float] = Field(title="Creditos requeridos")
  schedule: ScheduleCourse = Field(title="Horario")

  