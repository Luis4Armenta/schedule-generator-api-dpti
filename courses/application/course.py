from typing import Optional, List

from courses.domain.model.course import Course
from courses.domain.ports.courses_repository import CourseRepository

from courses.application.course_filter.filter import CourseFilter, CourseChecker
from courses.application.course_filter.checkers import SubjectChecker, TeacherChecker, TimeChecker, AvailabilityChecker

class CourseService:
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



