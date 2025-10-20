import unittest
from courses.domain.model.course import Course
from courses.application.course_filter.checkers import TimeChecker

class TestTimeChecker(unittest.TestCase):

    def test_course_within_default_time_range(self):
        checker = TimeChecker()
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)
        self.assertTrue(checker.check(course))

    def test_course_outside_time_range(self):
        checker = TimeChecker()
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '06:00', 'end_time': '08:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_ending_after_time_range(self):
        checker = TimeChecker()
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '21:00', 'end_time': '23:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_starting_before_and_ending_within_time_range(self):
        checker = TimeChecker()
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '06:00', 'end_time': '08:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_with_multiple_sessions_all_within_time_range(self):
        checker = TimeChecker()

        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '12:00', 'end_time': '14:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)

    def test_course_with_multiple_sessions_one_outside_time_range(self):
        checker = TimeChecker()
        course = Course(
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
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_with_exact_boundary_times(self):
        checker = TimeChecker()
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '07:00', 'end_time': '22:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)
        
    # Pruebas con tiempos personalizados
    def test_course_with_custom_time_range_within(self):
        checker = TimeChecker(start_time='08:00', end_time='20:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '09:00', 'end_time': '19:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)

    def test_course_with_custom_time_range_outside_start(self):
        checker = TimeChecker(start_time='08:00', end_time='20:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '07:00', 'end_time': '09:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_with_custom_time_range_outside_end(self):
        checker = TimeChecker(start_time='08:00', end_time='20:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '19:00', 'end_time': '21:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)

    def test_course_with_custom_time_range_exact_start(self):
        checker = TimeChecker(start_time='08:00', end_time='20:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '08:00', 'end_time': '19:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)

    def test_course_with_custom_time_range_exact_end(self):
        checker = TimeChecker(start_time='08:00', end_time='20:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'WEDNESDAY', 'start_time': '09:00', 'end_time': '20:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)
        
    def test_course_with_multiple_sessions_all_within_custom_time_range(self):
        checker = TimeChecker(start_time='07:00', end_time='15:00')

        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '07:00', 'end_time': '09:00'},
            {'day': 'WEDNESDAY', 'start_time': '11:00', 'end_time': '13:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertTrue(result)

    def test_course_with_multiple_sessions_one_outside_custom_time_range(self):
        checker = TimeChecker(start_time='07:00', end_time='15:00')
        course = Course(
          career='C',
          course_availability=40,
          level='5',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '15:00', 'end_time': '17:00'}],
          semester='5',
          sequence='5CM50',
          shift='M',
          subject='PROGRAMACIÓN WEB',
          teacher='JOSÉ JUAN CARRILLO',
          teacher_positive_score=0.5
        )
        
        result = checker.check(course)

        self.assertFalse(result)
