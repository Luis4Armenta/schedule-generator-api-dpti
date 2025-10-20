import unittest
from unittest.mock import MagicMock
from courses.domain.model.course import Course, ScheduleCourse
from courses.application.course_filter.checkers import TeacherChecker
from typing import List
    
class TestTeacherChecker(unittest.TestCase):
    def test_course_with_excluded_teacher(self):
        checker = TeacherChecker(excluded_teachers=['DE LA PARRA MARÍA', 'PÉREZ LÓPEZ ADAUTO'])
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='DE LA PARRA MARÍA',
          teacher_positive_score=0.5
        )

        result = checker.check(course);
        
        self.assertFalse(result)

    def test_course_not_in_excluded_teachers(self):
        checker = TeacherChecker(excluded_teachers=['DE LA PARRA MARÍA', 'PÉREZ LÓPEZ ADAUTO'])
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='REDES Y CONECTIVIDAD',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)

    def test_course_with_different_case_and_whitespace(self):
        checker = TeacherChecker(["de la parra maría", "perez lopez adauto "])
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='FINANZAS',
          teacher='DE LA PARRA MARÍA',
          teacher_positive_score=0.5
        )

        result = checker.check(course)

        self.assertFalse(result)

    def test_course_not_in_excluded_teachers_with_different_case(self):
        checker = TeacherChecker(['de la parra maría', 'pérez lópez adauto'])
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROBABILIDAD',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )

        result = checker.check(course)
        self.assertTrue(result)

    def test_empty_excluded_teachers(self):
        checker = TeacherChecker([])
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)
        
        self.assertTrue(result)