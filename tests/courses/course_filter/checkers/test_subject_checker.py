import unittest
from unittest.mock import MagicMock
from courses.domain.model.course import Course, ScheduleCourse
from courses.application.course_filter.checkers import SubjectChecker
from typing import List
    
class TestSubjectChecker(unittest.TestCase):
    def test_course_in_excluded_subjects(self):
        checker = SubjectChecker(excluded_subjects=['LÓGICA DE PROGRAMACIÓN', 'PROGRAMACIÓN WEB'])
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

        result = checker.check(course);
        
        self.assertFalse(result)

    def test_course_not_in_excluded_subjects(self):
        checker = SubjectChecker(excluded_subjects=['LÓGICA DE PROGRAMACIÓN', 'PROGRAMACIÓN WEB'])
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
        checker = SubjectChecker(["finanzas", "resdes y conectividad "])
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
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )

        result = checker.check(course)

        self.assertFalse(result)

    def test_course_not_in_excluded_subjects_with_different_case(self):
        checker = SubjectChecker(["lógica de programación", "programación web"])
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

    def test_empty_excluded_subjects(self):
        checker = SubjectChecker([])
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