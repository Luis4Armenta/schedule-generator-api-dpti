from typing import List, Dict
from abc import ABC, abstractmethod

from courses.domain.model.course import Course

class CourseRepository(ABC):
  """Puerto (interfaz) para el repositorio de cursos - Arquitectura Hexagonal"""
  
  @abstractmethod
  def connect(self, options) -> None:
    """Establece conexión con el almacenamiento de datos"""
    pass
    
  @abstractmethod
  def get_courses(
      self,
      levels: List[str],
      career: str,
      semesters: List[str],
      subjects: List[str] = [],
      shifts: List[str] = ['M', 'V']
    ) -> List[Course]:
    """Obtiene cursos filtrados por criterios"""
    pass
  
  @abstractmethod
  def upsert_course(self, course: Course) -> bool:
    """Inserta o actualiza un curso"""
    pass
  
  @abstractmethod
  def insert_courses(self, courses: List[Course]) -> int:
    """Inserta múltiples cursos"""
    pass
  
  @abstractmethod
  def update_course_availability(self, sequence: str, subject: str, availability: int) -> bool:
    """Actualiza solo la disponibilidad de un curso"""
    pass
  
  @abstractmethod
  def get_downloaded_periods(self, career: str, plan: str, shift: str = None) -> Dict[str, float]:
    """Obtiene períodos descargados con sus timestamps para un turno específico"""
    pass
  
  @abstractmethod
  def set_downloaded_periods(self, career: str, plan: str, periods: List[int], shift: str, timestamp: float) -> None:
    """Registra períodos descargados con timestamp y turno"""
    pass
  
  @abstractmethod
  def check_missing_periods(self, career: str, plan: str, requested_periods: List[int], shift: str) -> List[int]:
    """Verifica qué períodos faltan o están desactualizados para un turno específico"""
    pass
  
  @abstractmethod
  def disconnect(self) -> None:
    """Cierra la conexión con el almacenamiento de datos"""
    pass

