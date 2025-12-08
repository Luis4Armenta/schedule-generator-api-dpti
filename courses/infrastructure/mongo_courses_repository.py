import os
import time

from pymongo import MongoClient
from typing import TypedDict, List

from courses.domain.model.course import Course
from courses.domain.ports.courses_repository import CourseRepository

from utils.text import generate_regex

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class MongoCourseRepository(CourseRepository):
  """Adaptador de persistencia para MongoDB - Arquitectura Hexagonal
  
  Implementa el puerto CourseRepository definido en el dominio.
  Este adaptador encapsula todos los detalles de MongoDB (conexión, queries, índices)
  permitiendo que la lógica de negocio permanezca agnóstica de la tecnología de BD.
  
  Patrón: Singleton para reutilizar la conexión MongoDB.
  """
  
  def connect(self) -> None:
    self.mongo_client = MongoClient(os.environ['MONGODB_CONNECTION_STRING'])
    self.database = self.mongo_client[os.environ['MONGODB_DATABASE']]
    self.course_collection = self.database['courses']

  def get_courses(
      self,
      levels: List[str],
      career: str,
      semesters: List[str],
      subjects: List[str] = [],
      shifts: List[str] = ['M', 'V']
    ) -> List[Course]:
    expression = generate_regex(levels, career, shifts, semesters)
    query = {
      "sequence": {
        "$regex": expression,
        "$options": 'i'
      }
    }
    
    if subjects:
      query['subject'] = {
        "$in": subjects
      }
    

    filtered_courses = self.course_collection.find(query)
    courses = [Course(**course) for course in filtered_courses]
    
    return courses

  
  def upsert_course(self, course: Course) -> bool:
    """Inserta o actualiza un curso usando sequence+subject como clave única"""
    try:
      filter_query = {
        'sequence': course.sequence,
        'subject': course.subject
      }
      
      course_dict = {
        'semester': course.semester,
        'career': course.career,
        'level': course.level,
        'plan': course.plan,
        'shift': course.shift,
        'sequence': course.sequence,
        'subject': course.subject,
        'teacher': course.teacher,
        'schedule': course.schedule,
        'course_availability': course.course_availability,
        'required_credits': course.required_credits,
        'teacher_positive_score': course.teacher_positive_score,
      }
      
      self.course_collection.update_one(
        filter_query,
        {'$set': course_dict},
        upsert=True
      )
      return True
    except Exception as e:
      print(f"Error upserting course: {e}")
      return False

  def insert_courses(self, courses: List[Course]) -> int:
    """Inserta múltiples cursos usando upsert"""
    count = 0
    for course in courses:
      if self.upsert_course(course):
        count += 1
    return count

  def update_course_availability(self, sequence: str, subject: str, availability: int) -> bool:
    """Actualiza solo la disponibilidad de un curso existente"""
    try:
      result = self.course_collection.update_one(
        {'sequence': sequence, 'subject': subject},
        {'$set': {'course_availability': availability}}
      )
      return result.modified_count > 0
    except Exception as e:
      print(f"Error updating availability: {e}")
      return False

  def get_downloaded_periods(self, career: str, plan: str, shift: str = None) -> dict:
    """Obtiene los períodos descargados con sus timestamps para carrera+plan+turno"""
    query = {'career': career, 'plan': plan}
    if shift:
      query['shift'] = shift
    
    metadata = self.database['course_metadata'].find_one(query)
    if not metadata:
      return {}
    return metadata.get('periods', {})

  def set_downloaded_periods(self, career: str, plan: str, periods: List[int], shift: str, timestamp: float) -> None:
    """Registra los períodos descargados con timestamp y turno"""
    # Obtener períodos existentes
    existing = self.get_downloaded_periods(career, plan, shift)
    
    # Actualizar con los nuevos períodos
    for period in periods:
      existing[str(period)] = timestamp
    
    self.database['course_metadata'].update_one(
      {'career': career, 'plan': plan, 'shift': shift},
      {'$set': {'periods': existing}},
      upsert=True
    )

  def check_missing_periods(self, career: str, plan: str, requested_periods: List[int], shift: str) -> List[int]:
    """Verifica qué períodos solicitados NO están descargados o están desactualizados (>7 días) para un turno específico"""
    downloaded = self.get_downloaded_periods(career, plan, shift)
    current_time = time.time()
    week_in_seconds = 7 * 24 * 60 * 60
    
    missing = []
    for period in requested_periods:
      period_str = str(period)
      if period_str not in downloaded:
        # Período nunca descargado para este turno
        missing.append(period)
      else:
        # Verificar si está desactualizado
        last_update = downloaded[period_str]
        if (current_time - last_update) > week_in_seconds:
          missing.append(period)
    
    return missing

  def disconnect(self) -> None:
    self.mongo_client.close()
    