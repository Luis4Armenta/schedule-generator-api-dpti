import unittest
from unittest.mock import MagicMock
from courses.domain.model.course import Course
from courses.domain.ports.courses_repository import CourseRepository
from courses.application.course import CourseService
from schedules.application.schedule import ScheduleService

class TestScheduleService(unittest.TestCase):
  def setUp(self):
    self.course1 = Course(
    career='C',
    course_availability=40,
    level='5',
    plan='21',
    required_credits=7,
    schedule=[
        {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
        {'day': 'WEDNESDAY', 'start_time': '07:00', 'end_time': '08:00'}
    ],
    semester='5',
    sequence='5CM50',
    shift='M',
    subject='PROGRAMACIÓN WEB',
    teacher='NONATO CUEVAS ERLY',
    teacher_positive_score=0.5
    )

    self.course2 = Course(
        career='C',
        course_availability=35,
        level='4',
        plan='21',
        required_credits=6,
        schedule=[
            {'day': 'TUESDAY', 'start_time': '09:00', 'end_time': '11:00'},
            {'day': 'THURSDAY', 'start_time': '10:00', 'end_time': '12:00'}
        ],
        semester='4',
        sequence='4CV40',
        shift='V',
        subject='BASES DE DATOS',
        teacher='GARCÍA LÓPEZ CARLOS',
        teacher_positive_score=0.7
    )

    self.course3 = Course(
        career='C',
        course_availability=30,
        level='3',
        plan='21',
        required_credits=5,
        schedule=[
            {'day': 'WEDNESDAY', 'start_time': '13:00', 'end_time': '15:00'},
            {'day': 'FRIDAY', 'start_time': '14:00', 'end_time': '16:00'}
        ],
        semester='3',
        sequence='3CM30',
        shift='M',
        subject='ALGORITMOS',
        teacher='PÉREZ MARTÍNEZ ANA',
        teacher_positive_score=0.9
    )

    self.course4 = Course(
        career='C',
        course_availability=25,
        level='2',
        plan='21',
        required_credits=4,
        schedule=[
            {'day': 'THURSDAY', 'start_time': '07:00', 'end_time': '09:00'},
            {'day': 'FRIDAY', 'start_time': '10:00', 'end_time': '12:00'}
        ],
        semester='2',
        sequence='2CV20',
        shift='V',
        subject='ESTRUCTURAS DE DATOS',
        teacher='DÍAZ SÁNCHEZ MARÍA',
        teacher_positive_score=0.8
    )

    self.course5 = Course(
        career='C',
        course_availability=20,
        level='1',
        plan='21',
        required_credits=3,
        schedule=[
            {'day': 'MONDAY', 'start_time': '11:00', 'end_time': '13:00'}
        ],
        semester='1',
        sequence='1CM10',
        shift='M',
        subject='INTRODUCCIÓN A LA PROGRAMACIÓN',
        teacher='RODRÍGUEZ GONZÁLEZ LUIS',
        teacher_positive_score=0.6
    )

    self.course6 = Course(
        career='C',
        course_availability=15,
        level='6',
        plan='21',
        required_credits=8,
        schedule=[
            {'day': 'TUESDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'THURSDAY', 'start_time': '13:00', 'end_time': '15:00'}
        ],
        semester='6',
        sequence='6CV60',
        shift='V',
        subject='SISTEMAS OPERATIVOS',
        teacher='LOPEZ FERNÁNDEZ JUAN',
        teacher_positive_score=0.4
    )

    self.course7 = Course(
        career='C',
        course_availability=0,
        level='7',
        plan='21',
        required_credits=9,
        schedule=[
            {'day': 'MONDAY', 'start_time': '10:00', 'end_time': '12:00'},
            {'day': 'WEDNESDAY', 'start_time': '14:00', 'end_time': '16:00'}
        ],
        semester='7',
        sequence='7CM70',
        shift='M',
        subject='INTELIGENCIA ARTIFICIAL',
        teacher='NONATO CUEVAS ERLY',
        teacher_positive_score=0.5
    )

    self.course8 = Course(
        career='C',
        course_availability=50,
        level='8',
        plan='21',
        required_credits=10,
        schedule=[
            {'day': 'THURSDAY', 'start_time': '15:00', 'end_time': '17:00'},
            {'day': 'FRIDAY', 'start_time': '08:00', 'end_time': '10:00'}
        ],
        semester='8',
        sequence='8CM80',
        shift='M',
        subject='MÁQUINAS Y HERRAMIENTAS',
        teacher='GARCÍA LÓPEZ CARLOS',
        teacher_positive_score=0.6
    )

    self.course9 = Course(
        career='C',
        course_availability=45,
        level='7',
        plan='21',
        required_credits=11,
        schedule=[
            {'day': 'WEDNESDAY', 'start_time': '09:00', 'end_time': '11:00'},
            {'day': 'FRIDAY', 'start_time': '11:00', 'end_time': '13:00'}
        ],
        semester='7',
        sequence='7CV70',
        shift='V',
        subject='PROGRAMACIÓN WEB',
        teacher='RODRÍGUEZ GONZÁLEZ LUIS',
        teacher_positive_score=0.7
    )

    self.course10 = Course(
        career='C',
        course_availability=12,
        level='4',
        plan='21',
        required_credits=12,
        schedule=[
            {'day': 'TUESDAY', 'start_time': '10:00', 'end_time': '12:00'},
            {'day': 'THURSDAY', 'start_time': '12:00', 'end_time': '14:00'}
        ],
        semester='4',
        sequence='4CM40',
        shift='M',
        subject='REDES DE COMPUTADORAS',
        teacher='LOPEZ FERNÁNDEZ JUAN',
        teacher_positive_score=0.8
    )
    
    self.courses = [
      self.course1,
      self.course2,
      self.course3,
      self.course4,
      self.course5,
      self.course6,
      self.course7,
      self.course8,
      self.course9,
      self.course10,
      ]
    
    self.course_service = MagicMock(spec=CourseService)
    # self.course_repository = MagicMock(spec=CourseRepository)
    
    
  def test_correct_len_of_courses_per_schedule(self):
    self.course_service.filter_coruses.return_value = self.courses

    schedule_service = ScheduleService(self.course_service)
    
    result = schedule_service.generate_schedules(
          levels=['5'],
          career='C',
          extra_subjects = [],
          required_subjects = [],
          semesters=['5'],
          start_time='07:00',
          end_time='22:00',
          excluded_teachers=[],
          excluded_subjects=[],
          min_course_availability=[],
          n=2,
          credits=20,
          max_results= 20
        );
    
    for schedule in result:
      self.assertEqual(len(schedule.courses), 2);
    
    for schedule in result:
      for course in schedule.courses:
        for session in course.schedule:
          self.assertGreaterEqual(session['start_time'], '07:00')
        
        self.assertEqual(course.career, 'C')

      