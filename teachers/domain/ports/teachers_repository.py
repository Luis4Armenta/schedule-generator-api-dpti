from typing import Optional
from abc import ABC, abstractmethod

from teachers.domain.model.teacher import Teacher

class TeacherRepository(ABC):
  @abstractmethod
  def connect(self, options) -> None:
    pass
    
  @abstractmethod
  def get_teacher(self, teacher_name: str) -> Optional[Teacher]:
    pass
  
  @abstractmethod
  def disconnect(self) -> None:
    pass

