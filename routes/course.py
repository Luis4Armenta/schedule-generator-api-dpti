from typing import List
from fastapi import APIRouter
from schemas.schedule import CoursesRequest
from courses.domain.model.course import Course
from courses.application.course import CourseService


router = APIRouter()

@router.get(
  '/courses/',
  summary='Obtener cursos',
  response_description="Una lista de cursos se encuentran dentro de los parámetros dados.",
  description='Obten una lista de cursos que cumplan con los parámetros dados.'
)
def get_courses(request: CoursesRequest) -> List[Course]:
  course_service = CourseService(router.courses)
  
  filtered_courses = course_service.get_courses(request.career, request.levels, request.semesters, request.shifts)
  
  return filtered_courses
