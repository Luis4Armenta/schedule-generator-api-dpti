from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
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
