# -*- coding: utf-8 -*-
import sys
import time
from typing import List

from fastapi import APIRouter, HTTPException

from schedules.domain.model.schedule import Schedule
from schemas.schedule import (
    ScheduleGeneratorRequest,
    ScheduleDownloadRequest,
    AvailabilityDownloadRequest,
    ScheduleDownloadResponse,
    AvailabilityDownloadResponse,
    CourseScheduleInfo,
)

from courses.application.course import CourseService
from schedules.application.schedule import ScheduleService
from schedules.application.scraper_service import SAESScraperService
from routes.login import login_store, LOGIN_TTL_SECONDS

router = APIRouter()

@router.post(
  '/schedules/',
  summary='Generar horarios',
  response_description="Una lista ordenada de 20 horarios generados de mejor puntuados a peor puntuados."
)
async def generate_schedules(request: ScheduleGeneratorRequest) -> List[Schedule]:
  '''
  A partir de los parametros dados genera una coleccion de horarios que cumplan con ellos.
  
  - **career**: letra asignada a la carrera para la que se generara el horario.
  - **levels**: niveles de los cursos que se tendran en cuenta para formar los horarios.
  - **semesters**: semestres que se tendran en cuenta para formar los horarios.
  - **start_time**: hora a partir de la que iniciaran los horarios.
  - **end_time**: hora maxima a la que finalizaran los horarios.
  - **shifts**: turnos que podran integrar los horarios.
  - **length**: numero de asignaturas con las que cumplira cada horario.
  - **excluded_teachers**: profesores que seran excluidos de los horarios generados.
  - **excluded_subjects**: nombres de asignaturas que seran excluidas de los horarios generados.
  - **required_subjects**: asignaturas que tienen que aparecer en los horarios obligatoriamente.
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

@router.post(
  '/schedules/download',
  summary='Descargar horarios desde SAES',
  response_description="Lista de horarios descargados con su disponibilidad",
  response_model=ScheduleDownloadResponse
)
async def download_schedules_endpoint(request: ScheduleDownloadRequest) -> ScheduleDownloadResponse:
  '''
  Descarga horarios directamente desde SAES usando las cookies de autenticacion.
  Requiere un login exitoso previo.
  
  - **session_id**: ID de sesion obtenido del login
  - **career**: Codigo de carrera
  - **career_plan**: Codigo del plan de estudios
  - **plan_period**: Lista de periodos a descargar (1-10)
  - **shift**: Turno especifico (opcional)
  - **sequence**: Secuencia especifica (opcional)
  '''
  try:
    sys.stderr.write(f"[Endpoint] /schedules/download session_id={request.session_id}\n")
    sys.stderr.flush()
    sys.stderr.write(f"[Endpoint] login_store keys actuales={list(login_store.keys())}\n")
    sys.stderr.flush()
    # Verificar que existe la sesion de login
    stored = login_store.get(request.session_id)
    if not stored:
      sys.stderr.write(f"[Endpoint] Sesion {request.session_id} no encontrada en login_store\n")
      sys.stderr.flush()
      raise HTTPException(
        status_code=401,
        detail="Sesion no encontrada o expirada. Por favor, realiza login nuevamente."
      )
    
    # Verificar TTL
    now = time.time()
    created_at = stored.get('created_at', 0)
    if now - created_at > LOGIN_TTL_SECONDS:
      sys.stderr.write(f"[Endpoint] Sesion {request.session_id} expirada TTL={LOGIN_TTL_SECONDS}s\n")
      sys.stderr.flush()
      try:
        del login_store[request.session_id]
      except Exception:
        pass
      raise HTTPException(
        status_code=401,
        detail="La sesion ha expirado. Por favor, realiza login nuevamente."
      )
    
    # Obtener cookies
    cookies = stored.get('cookies', {})
    session_id = cookies.get('ASP.NET_SessionId')
    token = cookies.get('.ASPXFORMSAUTH')
    
    if not session_id or not token:
      sys.stderr.write(f"[Endpoint] Cookies faltantes session_id={session_id} token={token}\n")
      sys.stderr.flush()
      raise HTTPException(
        status_code=401,
        detail="Cookies de autenticacion no encontradas. Por favor, realiza login nuevamente."
      )
    
    # Inicializar scraper
    scraper = SAESScraperService(session_id=session_id, token=token)
    
    # Descargar horarios
    courses = scraper.download_schedules(
      career=request.career,
      career_plan=request.career_plan,
      plan_periods=request.plan_period,
      shift=request.shift,
      sequence=None
    )
    sys.stderr.write(f"[Endpoint] Cursos descargados={len(courses)}\n")
    sys.stderr.flush()
    
    # Descargar disponibilidad
    availabilities = scraper.download_availability(
      career=request.career,
      career_plan=request.career_plan
    )
    sys.stderr.write(f"[Endpoint] Disponibilidades descargadas={len(availabilities)}\n")
    sys.stderr.flush()
    
    # Combinar horarios con disponibilidad
    availability_map = {
      f"{a['sequence']}_{a['subject']}": a['availability']
      for a in availabilities
    }
    
    course_info_list = []
    for course in courses:
      key = f"{course['sequence']}_{course['subject']}"
      course['availability'] = availability_map.get(key)
      course_info_list.append(CourseScheduleInfo(**course))
    
    return ScheduleDownloadResponse(
      status="success",
      message=f"Se descargaron {len(course_info_list)} cursos con su disponibilidad",
      courses=course_info_list,
      total_courses=len(course_info_list)
    )
    
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail=f"Error al descargar horarios: {str(e)}"
    )


@router.post(
  '/schedules/download-availability',
  summary='Descargar disponibilidad de cursos desde SAES',
  response_description="Lista de disponibilidades actualizadas",
  response_model=AvailabilityDownloadResponse
)
async def download_availability_endpoint(request: AvailabilityDownloadRequest) -> AvailabilityDownloadResponse:
  '''
  Descarga la disponibilidad de cursos desde SAES.
  Debe ejecutarse con cada login para obtener datos actualizados.
  
  - **session_id**: ID de sesion obtenido del login
  - **career**: Codigo de carrera
  - **career_plan**: Codigo del plan de estudios
  '''
  try:
    # Verificar sesion
    stored = login_store.get(request.session_id)
    if not stored:
      raise HTTPException(
        status_code=401,
        detail="Sesion no encontrada o expirada. Por favor, realiza login nuevamente."
      )
    
    # Verificar TTL
    now = time.time()
    created_at = stored.get('created_at', 0)
    if now - created_at > LOGIN_TTL_SECONDS:
      try:
        del login_store[request.session_id]
      except Exception:
        pass
      raise HTTPException(
        status_code=401,
        detail="La sesion ha expirado. Por favor, realiza login nuevamente."
      )
    
    # Obtener cookies
    cookies = stored.get('cookies', {})
    session_id = cookies.get('ASP.NET_SessionId')
    token = cookies.get('.ASPXFORMSAUTH')
    
    if not session_id or not token:
      raise HTTPException(
        status_code=401,
        detail="Cookies de autenticacion no encontradas. Por favor, realiza login nuevamente."
      )
    
    # Inicializar scraper
    scraper = SAESScraperService(session_id=session_id, token=token)
    
    # Descargar disponibilidad
    availabilities = scraper.download_availability(
      career=request.career,
      career_plan=request.career_plan
    )
    
    return AvailabilityDownloadResponse(
      status="success",
      message=f"Se descargaron {len(availabilities)} disponibilidades",
      availabilities=availabilities,
      total_updated=len(availabilities)
    )
    
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=500,
      detail=f"Error al descargar disponibilidad: {str(e)}"
    )
