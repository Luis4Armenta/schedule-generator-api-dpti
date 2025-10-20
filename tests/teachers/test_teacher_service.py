import unittest
from unittest.mock import MagicMock
from teachers.application.teacher import TeacherService
from teachers.domain.model.teacher import Teacher, Comment, PyObjectId

class MockTeacherRepository:
    def get_teacher(self, teacher_name):
        pass

class TestTeacherService(unittest.TestCase):

    def test_get_teacher_unassigned(self):
        mock_repository = MockTeacherRepository()
        service = TeacherService(repository=mock_repository)

        # Caso de prueba para "SIN ASIGNAR"
        teacher = service.get_teacher('SIN ASIGNAR')
        self.assertEqual(teacher.name, 'SIN ASIGNAR')
        self.assertEqual(teacher.url, 'https://foroupiicsa.net/diccionario/buscar/')
        self.assertEqual(teacher.positive_score, 0.5)
        self.assertEqual(len(teacher.comments), 0)

    def test_get_teacher_from_repo(self):
        comment1 =  Comment(
            date='24, abril, 2024',
            dislikes=0,
            likes=0,
            subject='PROGRAMACIÓN WEB',
            text='Es un buen profesor.'
          )

        comment2 = Comment(
            date='25, Marzo, 2024',
            dislikes= 20,
            likes=1,
            subject='DISEÑO DE BASES DE DATOS',
            text='Es realmente odioso.',
            negative_score=0.9,
            positive_score=0.0,
            neutral_score=0.1,
          )
        
        teacherMock = Teacher(
            _id=PyObjectId('666f6f2d6261722d71757578'),
            name='John Doe',
            positive_score=0.8,
            url='https://foroupiicsa.net/diccionario/buscar/JOHN+DOE',
            comments=[comment1, comment2],
          )

        mock_repository = MockTeacherRepository()
        mock_repository.get_teacher = MagicMock(return_value=teacherMock)
        service = TeacherService(repository=mock_repository)

        # Caso de prueba para un profesor que está en el repositorio
        teacher = service.get_teacher('John Doe')
        self.assertEqual(teacher.name, 'John Doe')
        self.assertEqual(teacher.url, 'https://foroupiicsa.net/diccionario/buscar/JOHN+DOE')
        self.assertEqual(len(teacher.comments), 2)
        self.assertEqual(teacher.comments[0], comment1)
        self.assertEqual(teacher.comments[1], comment2)

    def test_get_teacher_not_in_repo(self):
        mock_repository = MockTeacherRepository()
        mock_repository.get_teacher = MagicMock(return_value=None)
        service = TeacherService(repository=mock_repository)

        # Caso de prueba para un profesor que no está en el repositorio
        teacher = service.get_teacher('Jane Doe')
        self.assertEqual(teacher.name, 'JANE DOE')
        self.assertEqual(str(teacher.url), 'https://foroupiicsa.net/diccionario/buscar/JANE+DOE')
        self.assertEqual(len(teacher.comments), 0)
