from typing import Optional
from functools import cache

from utils.text import clean_name, get_url_for_teacher
from teachers.domain.model.teacher import Teacher
from teachers.domain.ports.teachers_repository import TeacherRepository


class TeacherService:
  def __init__(
      self,
      repository: TeacherRepository,
    ):
    self.teacher_repository = repository
  
  @cache
  def get_teacher(self, teacher_name: str) -> Optional[Teacher]:
    teacher_name = clean_name(teacher_name)
    
    
    # If the teacher is Unassigned
    if teacher_name == 'SIN ASIGNAR':
      return Teacher(
        name='SIN ASIGNAR',
        comments=[],
        positive_score=0.5,
        url='https://foroupiicsa.net/diccionario/buscar/'
      )
    else:
      # else find in the teacher repo
      teacher = self.teacher_repository.get_teacher(teacher_name)
      
      # if teacher was found in the teacher repo
      if teacher is not None:
        return teacher
      else:
        teacher: Optional[Teacher] = Teacher(
            name=teacher_name,
            comments=[],
            positive_score=0.5,
            url=get_url_for_teacher(teacher_name)
          )
        
        return teacher
        