import os
import unittest
from unittest.mock import MagicMock
from teachers.infrastructure.mongo_teachers_repository import MongoTeachersRepository, Teacher
from teachers.domain.model.teacher import PyObjectId

class TestMongoTeachersRepository(unittest.TestCase):


    def test_get_teacher_found(self):
        # Simular la conexión y la colección de MongoDB
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            '_id': '123',
            'name': 'John Doe',
            'url': 'https://example.com',
            'comments': [],
            'positive_score': 0.8
        }

        mock_database = MagicMock()
        mock_database['teachers'] = mock_collection

        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_database

        # Crear una instancia de MongoTeachersRepository con el cliente simulado
        repository = MongoTeachersRepository()
        repository.mongo_client = mock_client
        repository.teachers_collection = mock_collection;

        # Llamar a get_teacher con un nombre de profesor existente
        teacher = repository.get_teacher('John Doe')

        # Verificar que se devuelve el profesor esperado
        self.assertIsInstance(teacher, Teacher)
        self.assertEqual(teacher.name, 'John Doe')
        self.assertEqual(teacher.url, 'https://example.com')
        self.assertEqual(teacher.comments, [])
        self.assertEqual(teacher.positive_score, 0.8)
# 
    def test_get_teacher_not_found(self):
        # Simular la conexión y la colección de MongoDB
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        mock_database = MagicMock()
        mock_database['teachers'] = mock_collection

        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_database


        # Crear una instancia de MongoTeachersRepository con el cliente simulado
        repository = MongoTeachersRepository()
        repository.mongo_client = mock_client
        repository.teachers_collection = mock_collection;

        # Llamar a get_teacher con un nombre de profesor inexistente
        teacher = repository.get_teacher('Jane Doe')

        # Verificar que se devuelve None
        self.assertIsNone(teacher)
