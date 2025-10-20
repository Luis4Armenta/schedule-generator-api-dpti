from typing import List

from courses.domain.model.course import Course

from courses.application.course_filter.checkers import CourseChecker
  
class CourseFilter:
  def __init__(self, checkers: List[CourseChecker]):
    self.checkers = checkers
    
  def filter_courses(self, courses: List[Course]) -> List[Course]:
    filtered_courses: List[Course] = []
    
    
    for course in courses:
      
      accepted_course: bool = True
      for checker in self.checkers:
        if not checker.check(course):
          accepted_course = False
          break
          
      if accepted_course:
        filtered_courses.append(course)
    
    return filtered_courses