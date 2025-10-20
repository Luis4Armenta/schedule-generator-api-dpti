from statistics import mean
from typing import List, Tuple, Optional

from courses.domain.model.course import Course
from courses.application.course import CourseService
from schedules.domain.model.schedule import Schedule

class ScheduleService:
    def __init__(
        self,
        course_service: CourseService
      ):
        self.course_service = course_service

    def generate_schedules(
        self,
        levels: List[str],
        career: str,
        extra_subjects: List[Tuple[str, str]],
        required_subjects: List[Tuple[str, str]],
        semesters: List[str],
        start_time: Optional[str],
        end_time: Optional[str],
        excluded_teachers: List[str],
        excluded_subjects: List[str],
        min_course_availability: int,
        n: int,
        credits: float,
        max_results: int = 20
    ) -> List[Schedule]:
        def backtrack(schedule: List[Course], start_index: int):
            # Verificar si se ha alcanzado el tamaño objetivo del horario
            if len(schedule) == n:
                schedule_subjects = [course.subject for course in schedule]

                if all(required_subject in schedule_subjects for required_subject in required_name_subjects):
                    # Calcular la polaridad promedio de los profesores en el horario
                    teachers_positive_score: List[float] = []
                    credits_required: float = 0
                    for course in schedule:
                        teachers_positive_score.append(
                            course.teacher_positive_score)
                        credits_required = credits_required + course.required_credits
                    
                    if credits_required <= credits:
                      schedule_result = Schedule(
                          avg_positive_score=mean(teachers_positive_score),
                          courses=schedule,
                          total_credits_required=credits_required
                      )
                      schedules.append(schedule_result)
                    return
                else:
                    return

            # Iterar sobre los cursos regulares, comenzando desde el índice de inicio
            for i in range(start_index, len(courses)):
                if is_valid(schedule, courses[i]):
                    schedule.append(courses[i])
                    backtrack(schedule, i + 1)
                    schedule.pop()

        # Verificar si un curso es válido para agregar al horario actual
        def is_valid(schedule: List[Course], course: Course) -> bool:
            for existing_course in schedule:
                if has_overlap(existing_course, course) or existing_course.subject == course.subject:
                    return False
            return True

        # Verificar si dos cursos tienen superposición en su horario
        def has_overlap(course1: Course, course2: Course) -> bool:
            for session1 in course1.schedule:
                for session2 in course2.schedule:
                    if session1['day'] == session2['day']:
                        session1_start, session1_end = session1['start_time'], session1['end_time']
                        session2_start, session2_end = session2['start_time'], session2['end_time']

                        if not (session1_end <= session2_start or session1_start >= session2_end):
                            return True
            return False


        courses = self._get_courses(
          levels=levels,
          career=career,
          extra_subjects=extra_subjects,
          required_subjects=required_subjects,
          semesters=semesters,
        )
      
        courses = self._filter_courses(
          courses=courses,
          start_time=start_time,
          end_time=end_time,
          excluded_teachers=excluded_teachers,
          excluded_subjects=excluded_subjects,
          min_course_availability=min_course_availability
        )
        
        required_name_subjects = [required_subject[1] for required_subject in required_subjects]
        

        schedules: List[Schedule] = []  # Lista para almacenar los horarios generados
        # Iniciar la generación de horarios desde un horario vacío y el índice de inicio 0
        backtrack([], 0)
        
        schedules = sorted(schedules, key=lambda x: x.avg_positive_score, reverse=True)
        
        r = [] 
        for value, schedule in enumerate(schedules[:max_results]):
          schedule.option = value
          r.append(schedule)
        return r
      
    def _get_courses(
      self,
      career: str,
      levels: List[str],
      semesters: List[str],
      required_subjects: List[Tuple[str, str]],
      extra_subjects: List[Tuple[str, str]]
    ) -> List[Course]:
      courses: List[Course] = self.course_service.get_courses(
        career,
        levels,
        semesters
      )

      for required_subject in required_subjects:
        required_subject_sequence = required_subject[0]
        required_subject = required_subject[1]
        
        
        required_subject_level = required_subject_sequence[0]
        required_subject_semester = required_subject_sequence[3]
        
        if (
            not any(required_subject_level == level for level in levels) or
            not any(required_subject_semester == semester for semester in semesters)
          ):
            courses = courses + self.course_service.get_courses_by_subject(
              sequence=required_subject_sequence,
              subject=required_subject,
            )
            
      
      for extra_subject in extra_subjects:
        extra_subject_sequence = extra_subject[0]
        extra_subject = extra_subject[1]
        
        
        extra_subject_level = extra_subject_sequence[0]
        extra_subject_semester = extra_subject_sequence[3]
        
        if (
            not any(extra_subject_level == level for level in levels) or
            not any(extra_subject_semester == semester for semester in semesters)
          ):
            courses = courses + self.course_service.get_courses_by_subject(
              sequence=extra_subject_sequence,
              subject=extra_subject,
            )
            
      return courses
    
    def _filter_courses(
      self,
      courses: List[Course],
      start_time: Optional[str],
      end_time: Optional[str],
      min_course_availability: int = 1,
      excluded_teachers: List[str] = [],
      excluded_subjects: List[str] = [],
    ):
      return self.course_service.filter_coruses(
        courses=courses,
        start_time=start_time,
        end_time=end_time,
        excluded_teachers=excluded_teachers,
        excluded_subjects=excluded_subjects,
        min_course_availability=min_course_availability
      )