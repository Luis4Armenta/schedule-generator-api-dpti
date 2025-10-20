import unittest
from unittest.mock import MagicMock
from courses.application.course_filter.filter import CourseFilter
from courses.domain.model.course import Course
from courses.application.course_filter.checkers import CourseChecker

class TestCourseFilter(unittest.TestCase):

    def setUp(self):
        self.checker1 = MagicMock(spec=CourseChecker)
        self.checker2 = MagicMock(spec=CourseChecker)
        self.filter = CourseFilter([self.checker1, self.checker2])
        
        self.course1 = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '06:00', 'end_time': '07:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        self.course2 = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '06:00', 'end_time': '07:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='LÓGICA DE PROGRAMACIÓN',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        self.course3 = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '06:00', 'end_time': '07:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='ESTRUCTURAS DE DATOS',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
    
    def test_filter_courses_all_pass(self):
        
        self.checker1.check.return_value = True
        self.checker2.check.return_value = True
        
        result = self.filter.filter_courses([self.course1, self.course2])
        # 
        self.assertEqual(result, [self.course1, self.course2])
        # self.checker1.check.assert_called_with(self.course1)
        # self.checker1.check.assert_called_with(self.course2)
        # self.checker2.check.assert_called_with(self.course1)
        # self.checker2.check.assert_called_with(self.course2)

    def test_filter_courses_one_fails(self):
        
        self.checker1.check.side_effect = [True, False]
        self.checker2.check.return_value = True
        
        result = self.filter.filter_courses([self.course1, self.course2])
        
        self.assertEqual(result, [self.course1])
        # self.checker1.check.assert_called_with(self.course1)
        # self.checker1.check.assert_called_with(self.course2)
        # self.checker2.check.assert_called_with(self.course1)

    def test_filter_courses_all_fail(self):
        
        self.checker1.check.return_value = False
        self.checker2.check.return_value = True
        
        result = self.filter.filter_courses([self.course1, self.course2])
        
        self.assertEqual(result, [])
        # self.checker1.check.assert_called_with(self.course1)
        # self.checker1.check.assert_called_with(self.course2)

    def test_filter_courses_mixed_results(self):
        self.checker1.check.side_effect = [True, False, True]
        self.checker2.check.side_effect = [True, True, True]
        
        result = self.filter.filter_courses([self.course1, self.course2, self.course3])
        
        self.assertEqual(result, [self.course1, self.course3])
        # self.checker1.check.assert_any_call(self.course1)
        # self.checker1.check.assert_any_call(self.course2)
        # self.checker1.check.assert_any_call(self.course3)
        # self.checker2.check.assert_any_call(self.course1)
        # self.checker2.check.assert_any_call(self.course2)
        # self.checker2.check.assert_any_call(self.course3)
