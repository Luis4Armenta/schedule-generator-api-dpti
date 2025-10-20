from typing import List
from abc import ABC, abstractmethod

from courses.domain.model.course import Course

class CourseRepository(ABC):
  @abstractmethod
  def connect(self, options) -> None:
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
    pass
  
  @abstractmethod
  def disconnect(self) -> None:
    pass

