from pydantic import BaseModel, Field
from courses.domain.model.course import Course
from typing import List, Optional

class Schedule(BaseModel):
  option: Optional[int] = Field("Opción", description="Número de opción")
  courses: List[Course] = Field(title="Cursos", description="Cursos que conforman el horario")
  avg_positive_score: float = Field(title="Puntaje positivo", description="Promedio del puntaje positivo de todos los profesores que imparten las asignaturas que conforman el horario.")
  total_credits_required: float = Field(title="Total de creditos requeridos", description="Creditones necesarios para meter el horario.")