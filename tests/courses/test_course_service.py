import os
import unittest
from unittest.mock import MagicMock, patch
from courses.domain.model.course import Course
from courses.application.course import CourseService
from courses.domain.ports.courses_repository import CourseRepository

class TestCourseService(unittest.TestCase):

    def setUp(self):
        self.course_repository = MagicMock(spec=CourseRepository)
        self.course_service = CourseService(self.course_repository)

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
          teacher='NONATO CUEVAS ERLY',
          teacher_positive_score=0.5
        )
        self.course2 = Course(
          career='C',
          course_availability=40,
          level='1',
          plan='21',
          required_credits=7,
          schedule=[
            {'day': 'MONDAY', 'start_time': '08:00', 'end_time': '10:00'},
            {'day': 'WEDNESDAY', 'start_time': '06:00', 'end_time': '07:00'}],
          semester='1',
          sequence='5CM50',
          shift='M',
          subject='LÓGICA DE PROGRAMACIÓN',
          teacher='CARRILLO JOSÉ JUAN',
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
          teacher='ADAUTO ARMANDO',
          teacher_positive_score=0.5
        )

    def test_filter_courses(self):
        courses = [self.course1, self.course2]

        with patch('courses.application.course_filter.checkers.SubjectChecker.check', return_value=True), \
             patch('courses.application.course_filter.checkers.TeacherChecker.check', return_value=True), \
             patch('courses.application.course_filter.checkers.TimeChecker.check', return_value=True), \
             patch('courses.application.course_filter.checkers.AvailabilityChecker.check', return_value=True):
            result = self.course_service.filter_coruses(
                courses,
                start_time='07:00',
                end_time='22:00',
                min_course_availability=1,
                excluded_teachers=['CARRILLO JESUS CARLOS'],
                excluded_subjects=['TEORÍA DE COMPUTACIÓN Y COMPILADORES']
            )
        
        self.assertEqual(result, courses)

    def test_get_courses(self):
        career = "Engineering"
        levels = ["1", "2"]
        semesters = ["1", "2"]
        shifts = ["M", "V"]
        courses = [self.course1, self.course2, self.course3]
        
        self.course_repository.get_courses.return_value = courses
        result = self.course_service.get_courses(career, levels, semesters, shifts)
        
        self.assertEqual(result, courses)
        self.course_repository.get_courses.assert_called_with(levels=levels, career=career, semesters=semesters, shifts=shifts)

    def test_get_courses_by_subject(self):
        sequence = "5CM50"
        subject = "PROGRAMACIÓN WEB"
        shifts = ["M", "V"]
        courses = [self.course1, self.course2, self.course3]
        
        self.course_repository.get_courses.return_value = [self.course1]
        result = self.course_service.get_courses_by_subject(sequence, subject, shifts)
        
        self.assertEqual(result, [self.course1])
        self.course_repository.get_courses.assert_called_with(levels=["5"], shifts=shifts, career="C", semesters=["5"], subjects=[subject])
