from abc import ABC, abstractmethod
from typing import List

from courses.domain.model.course import Course

from utils.text import clean_name

class CourseChecker(ABC):

  @abstractmethod
  def check(self, course: Course) -> bool:
    pass

class SubjectChecker(CourseChecker):
  def __init__(self, excluded_subjects: List[str]):
    self.excluded_subjects = [clean_name(excluded_subject) for excluded_subject in excluded_subjects]
    
  def check(self, course: Course) -> bool:
    subject_course: str = clean_name(course.subject)
    
    if subject_course in self.excluded_subjects:
      return False
    else:
      return True
    
class TimeChecker(CourseChecker):
  def __init__(self, start_time: str = '07:00', end_time: str = '22:00'):
    self.start_time = start_time
    self.end_time = end_time
    
  def check(self, course: Course) -> bool:    
    for session in course.schedule:
      if session['start_time'] < self.start_time or session['end_time'] > self.end_time:
        return False
    
    return True
  
class TeacherChecker(CourseChecker):
  def __init__(self, excluded_teachers: List[str] = []):
    self.excluded_teachers = [clean_name(excluded_teacher) for excluded_teacher in excluded_teachers]
    
  def check(self, course: Course) -> bool:
    teacher_name: str = clean_name(course.teacher)
    
    if teacher_name in self.excluded_teachers:
      return False
    else:
      return True
    
class AvailabilityChecker(CourseChecker):
  def __init__(self, min_availability = 1):
    self.min_availability = min_availability
    
  def check(self, course: Course) -> bool:
    
    if course.course_availability >= self.min_availability:
      return True
    else:
      return False