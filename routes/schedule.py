import time
from typing import List

from fastapi import APIRouter

from schedules.domain.model.schedule import Schedule
from schemas.schedule import ScheduleGeneratorRequest

from courses.application.course import CourseService
from schedules.application.schedule import ScheduleService

router = APIRouter()

@router.post(
  '/schedules/',
  summary='Generar horarios',
  response_description="Una lista ordenada de 20 horarios generados de mejor puntuados a peor puntuados."
)
async def generate_schedules(request: ScheduleGeneratorRequest) -> List[Schedule]:
  '''
  Apartir de los parámetros dados genera una colección de horarios que cumplan con ellos.
  
  - **career**: letra asignada a la carrera para la que se generara el horario.
  - **levels**: niveles de los cursos que se tendrán en cuenta para formar los horarios.
  - **semesters**: semestres que se tendrán en cuenta para formar los horarios.
  - **start_time**: hora apartir de la que iniciaran los horarios.
  - **end_time**: hora máxima a la que finalizarán los horarios.
  - **shifts**: turnos que podrán integrar los horarios.
  - **length**: número de asignaturas con las que cumplicara cada horario.
  - **excluded_teachers**: profesores que serán excluidos de los horarios generados.
  - **excluded_subjects**: nombres de asignaturas que serán excluidas de los horarios generados.
  - **required_subjects**: asginaturas que tienen que aparecen el los horarios obligatoriamente.
  - **extra_subjects**: asignaturas opcionales que amplian el conjunto de asignaturas posibles en un horario.
  '''
  start = time.time()
  course_service = CourseService(router.courses)

  schedule_service = ScheduleService(course_service)

  schedules = schedule_service.generate_schedules(
      levels=request.levels,
      career=request.career,
      extra_subjects=request.extra_subjects,
      required_subjects=request.required_subjects,
      semesters=request.semesters,
      start_time=request.start_time,
      end_time=request.end_time,
      excluded_teachers=request.excluded_teachers,
      excluded_subjects=request.excluded_subjects,
      min_course_availability=request.available_uses,
      n = request.length,
      credits=request.credits,
      max_results = 20
    )
  
  end = time.time()
  print("Time Taken: {:.6f}s".format(end-start))

  return schedules 