import unittest
from courses.domain.model.course import Course
from courses.application.course_filter.checkers import AvailabilityChecker

class TestAvailabilityChecker(unittest.TestCase):

    def test_course_meets_min_availability(self):
        checker = AvailabilityChecker(min_availability=1)
        course = Course(
          career='C',
          course_availability=2,
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
        self.assertTrue(checker.check(course))

    def test_course_below_min_availability(self):
        checker = AvailabilityChecker(min_availability=3)
        course = Course(
          career='C',
          course_availability=2,
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
        self.assertFalse(checker.check(course))

    def test_course_exact_min_availability(self):
        checker = AvailabilityChecker(min_availability=2)
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=2,
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
        self.assertTrue(checker.check(course))

    def test_course_with_zero_availability(self):
        checker = AvailabilityChecker(min_availability=1)
        course = Course(
          career='C',
          course_availability=0,
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
        self.assertFalse(checker.check(course))

    def test_course_with_high_min_availability(self):
        checker = AvailabilityChecker(min_availability=10)
        course = Course(
          career='C',
          course_availability=15,
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
        self.assertTrue(checker.check(course))