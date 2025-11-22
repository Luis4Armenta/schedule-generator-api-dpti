from typing import Optional, List

from courses.domain.model.course import Course
from courses.domain.ports.courses_repository import CourseRepository

from courses.application.course_filter.filter import CourseFilter, CourseChecker
from courses.application.course_filter.checkers import SubjectChecker, TeacherChecker, TimeChecker, AvailabilityChecker


class CourseService:
  """Servicio de Aplicación para Cursos - Arquitectura Hexagonal
  
  Orquesta casos de uso relacionados con cursos:
  - Filtrado de cursos según criterios
  - Obtención de cursos desde repositorio
  - Persistencia de cursos descargados
  - Gestión de cache por período
  
  Depende de CourseRepository (puerto), no de implementación específica.
  Esto permite testing con mocks y cambio de tecnología de BD sin modificar esta clase.
  """
  
  def __init__(
      self,
      course_repository: CourseRepository
    ):
    self.course_repository = course_repository
  
  def filter_coruses(
    self,
    courses: List[Course],
    start_time: Optional[str],
    end_time: Optional[str],
    min_course_availability: int = 1,
    excluded_teachers: List[str] = [],
    excluded_subjects: List[str] = [],
  ) -> List[Course]:
    checkers: List[CourseChecker] = [
      SubjectChecker(
        excluded_subjects=excluded_subjects
      ),
      TeacherChecker(
        excluded_teachers=excluded_teachers
      ),
      TimeChecker(
        start_time=start_time,
        end_time=end_time
      ),
      AvailabilityChecker(
        min_availability=min_course_availability
      )
    ]
    
    course_filter = CourseFilter(checkers)
    
    return course_filter.filter_courses(courses)


  def get_courses(
      self,
      career: str,
      levels: List[str],
      semesters: List[str],
      shifts: List[str] = ['M', 'V']
    ) -> List[Course]:
    
    return self.course_repository.get_courses(
      levels=levels,
      career=career,
      semesters=semesters,
      shifts=shifts,
    )
  
  def get_courses_by_subject(
      self,
      sequence: str,
      subject: str,
      shifts: List[str] = ['M', 'V'],
    ) -> List[Course]:
    level = sequence[0]
    career = sequence[1]
    semester = sequence[3]
    
    return self.course_repository.get_courses(
      levels=[level],
      shifts=shifts,
      career=career,
      semesters=[semester],
      subjects=[subject]
    )

  def upload_courses(self, courses: List[Course]) -> int:
    """Guarda cursos en MongoDB usando upsert"""
    return self.course_repository.insert_courses(courses)

  def update_availability(self, sequence: str, subject: str, availability: int) -> bool:
    """Actualiza solo la disponibilidad de un curso"""
    return self.course_repository.update_course_availability(sequence, subject, availability)

  def get_downloaded_periods(self, career: str, plan: str) -> dict:
    """Obtiene períodos descargados con timestamps"""
    return self.course_repository.get_downloaded_periods(career, plan)

  def set_downloaded_periods(self, career: str, plan: str, periods: List[int], timestamp: float) -> None:
    """Registra períodos descargados con timestamp"""
    from typing import List
    self.course_repository.set_downloaded_periods(career, plan, periods, timestamp)

  def check_missing_periods(self, career: str, plan: str, requested_periods: List[int]) -> List[int]:
    """Verifica qué períodos faltan o están desactualizados"""
    from typing import List
    return self.course_repository.check_missing_periods(career, plan, requested_periods)



