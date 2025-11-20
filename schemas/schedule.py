from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
import datetime

class Shift(str, Enum):
  morning = 'M'
  afternoon  = 'V'

class Career(str, Enum):
  C = 'C'
  A = 'A'
  F = 'F'
  I = 'I'
  N = 'N'
  S = 'S'
  T = 'T'

class Level(str, Enum):
  one = '1'
  two = '2'
  three = '3'
  four = '4'
  five = '5'
  six = '6'
  seven = '7'
  eight = '8'

class Semester(str, Enum):
  one = '1'
  two = '2'
  three = '3'
  four = '4'
  five = '5'
  six = '6'
  seven = '7'
  eight = '8'

class ScheduleGeneratorRequest(BaseModel):
  career: Career = Field(title="Carrera", description="Letra que identifica la carrera a la que perteneceran los horarios generados")
  levels: List[Level] = Field(title="Niveles", description="Arreglo de niveles a los que pertenecen los cursos que van a conformar los horarios generados.", min_items=1)
  semesters: List[Semester] = Field(title="Semestres", description="Arreglo de los emestres a los que pertencen los cursos que van a coformar los horarios generados", min_items=1)
  start_time: Optional[str] = Field(title="Hora de entrada", description="Que es lo más temprano que quieres inciar tus clases.", default='07:00')
  end_time: Optional[str] = Field(
    title="Hora de salida",
    description="Qué es lo más tarde a lo que finalizaran los horarios.",
    default='07:00'
  )
  length: int = Field(
    title="Número de asignaturas",
    description="Número de asignaturas que formaran parte de cada horario generado.",
    gt=2, lt=12
  )
  credits: float = Field(
    title="Creditos",
    description="Cantidad de creditos con los que cuenta el alumno para canjear",
    gt=0
  )
  available_uses: int = Field(
    title="Usos disponibles",
    description="Número de lugares disponibles por curso.",
    ge=0, le=40, default=1
  )
  excluded_teachers: List[str] = Field(
    title="Profesores excluidos",
    description="Arreglo de nombres de profesores que no se tomaran en cuenta para formar parte de los horarios generados.",
    min_items=0, default=[]
  )
  excluded_subjects: List[str] = Field(
    title="Asignaturas excluidas",
    description="Arreglo de nombres de asignaturas que no se tomaran en cuenta para formar parte de los horarios generados.",
    min_items= 0, default= []
  )
  required_subjects: List[Tuple[str, str]] = Field(
    title="Asignaturas requeridas",
    description="Utiliza este parámetro para forzar una o más asignaturas.",
    min_items=0, default=[]
  )
  extra_subjects: List[Tuple[str, str]] = Field(
    title="Asignaturas extra",
    description="Utiliza este parámetro para extender el conjunto de asignaturas capaces de formar parte de los horarios generados, incluyendo materias de otros semestres o turnos.",
    min_length=0, default=[]
  )
  
class CoursesRequest(BaseModel):
  career: Career = Field(title="Carrera", description="Letra que identifica la carrera")
  levels: List[Level] = Field(title="Niveles", description="Arreglo de los niveles al que pertenecen los cursos que se desean consultar.", min_items=1)
  semesters: List[Semester] = Field(title="Semestres", description="Arreglo de los semestre al que pertenecen los cursos que se desean consultar.", min_items=1)
  shifts: List[Shift] = Field(title="Turnos", description="Arreglo que turnos al que pertenecen los cursos que se desean consultar.", min_items=1, max_items=2, default=['M', 'V'])
  
  class Config:
    
    schema_extra = {
      "examples": [
          {
            "Obtener los cursos de una secuencia": {
            "summary": "Obten los cursos que se imparten en una secuencia",
            "description": '''Obten todos los cursos que se imparten en la secuencia 4CM40 (Nivel 4, de Ciencias de la informática en el turno matutino durante el semestre 4)''',
            "value": {
                "career": "C",
                "levels": ["4"],
                "semesters": ["4"],
                "shifts": ["M"]
              }
            },
            
            "Obtener dos semestres": {
              "summary": "Obten los cursos que se imparten en dos semestres diferentes.",
              "description": "Puedes representar varios turnos, niveles o semestres mediante arreglos",
              "value": {
                "career": "C",
                "levels": ["4", "5"],
                "semesters": ["4", "5"],
                "shifts": ["M", "V"]
              }
            }
          }
          
      ]
    }


class ScheduleDownloadRequest(BaseModel):
  """Modelo para solicitar la descarga de horarios desde SAES"""
  session_id: str = Field(description="ID de sesión obtenido del login exitoso")
  career: str = Field(description="Código de carrera")
  career_plan: str = Field(description="Código del plan de estudios")
  plan_period: List[int] = Field(description="Lista de períodos (1-10)", min_items=1, max_items=10)
  shift: Optional[str] = Field(default=None, description="Turno específico (opcional)")

  class Config:
    schema_extra = {
      "example": {
        "session_id": "ae3f8c1b2d",
        "career": "C",
        "career_plan": "CI-2020",
        "plan_period": [4],
        "shift": "M"
      }
    }


class AvailabilityDownloadRequest(BaseModel):
  """Modelo para solicitar la descarga de disponibilidad desde SAES"""
  session_id: str = Field(description="ID de sesión obtenido del login exitoso")
  career: str = Field(description="Código de carrera")
  career_plan: str = Field(description="Código del plan de estudios")


class CourseScheduleInfo(BaseModel):
  """Información de un curso descargado"""
  sequence: str
  subject: str
  teacher: str
  schedule: List[Dict[str, str]]
  availability: Optional[int] = None

  class Config:
    schema_extra = {
      "example": {
        "sequence": "4CM40",
        "subject": "ESTRUCTURA DE DATOS",
        "teacher": "PEREZ LOPEZ JUAN",
        "schedule": [
          {"day": "Monday", "start_time": "07:00", "end_time": "08:30"},
          {"day": "Wednesday", "start_time": "07:00", "end_time": "08:30"}
        ],
        "availability": 12
      }
    }


class ScheduleDownloadResponse(BaseModel):
  """Respuesta de descarga de horarios"""
  status: str
  message: str
  courses: List[CourseScheduleInfo]
  total_courses: int

  class Config:
    schema_extra = {
      "example": {
        "status": "success",
        "message": "Se descargaron 3 cursos con su disponibilidad",
        "total_courses": 3,
        "courses": [
          {
            "sequence": "4CM40",
            "subject": "ESTRUCTURA DE DATOS",
            "teacher": "PEREZ LOPEZ JUAN",
            "schedule": [
              {"day": "Monday", "start_time": "07:00", "end_time": "08:30"},
              {"day": "Wednesday", "start_time": "07:00", "end_time": "08:30"}
            ],
            "availability": 12
          },
          {
            "sequence": "4CM40",
            "subject": "MATEMATICAS DISCRETAS",
            "teacher": "GOMEZ RAMIREZ ANA",
            "schedule": [
              {"day": "Tuesday", "start_time": "09:00", "end_time": "10:30"},
              {"day": "Thursday", "start_time": "09:00", "end_time": "10:30"}
            ],
            "availability": 5
          },
          {
            "sequence": "4CM40",
            "subject": "INGLES IV",
            "teacher": "LOPEZ DIAZ MARIA",
            "schedule": [
              {"day": "Friday", "start_time": "11:00", "end_time": "12:30"}
            ],
            "availability": 8
          }
        ]
      }
    }


class AvailabilityDownloadResponse(BaseModel):
  """Respuesta de descarga de disponibilidad"""
  status: str
  message: str
  availabilities: List[Dict[str, Any]]
  total_updated: int
