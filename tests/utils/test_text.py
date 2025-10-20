import unittest
from unittest.mock import patch

from utils.text import clean_name, generate_regex, get_url_for_teacher

class TestCleanName(unittest.TestCase):
  def test_clean_name(self):
    # Caso de prueba 1: Cadena con caracteres especiales y espacios innecesarios
    self.assertEqual(clean_name("Café & Chocolaté"), "CAFE CHOCOLATE")
    # Caso de prueba 2: Cadena con caracteres especiales, números y múltiples espacios
    self.assertEqual(clean_name("¡Hola! 123 456"), "HOLA")
    # Caso de prueba 3: Cadena con solo caracteres alfabéticos y espacios
    self.assertEqual(clean_name("  hola mundo "), "HOLA MUNDO")
    # Caso de prueba 4: Cadena vacía
    self.assertEqual(clean_name(""), "")
    # Caso de prueba 5: Cadena con solo espacios
    self.assertEqual(clean_name("      "), "")
    # Caso de prueba 6: Cadena con solo caracteres especiales
    self.assertEqual(clean_name("!@#$%"), "")


class TestGenerateRegex(unittest.TestCase):
    def test_one_semester_one_shift(self):
      levels = ['5']
      career = 'C'
      shifts = ['M']
      semesters = ['5']

      expected_regex =  r'^[5][C][M][5][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)

    def test_one_semester_two_shifts(self):
      levels = ['5']
      career = 'C'
      shifts = ['M', 'V']
      semesters = ['5']

      expected_regex =  r'^[5][C][M|V][5][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)

    def test_two_semester_one_shifts(self):
      levels = ['5', '6']
      career = 'C'
      shifts = ['M']
      semesters = ['5', '6']
    
      expected_regex =  r'^[5|6][C][M][5|6][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)

    def test_two_semester_two_shifts(self):
      levels = ['5', '6']
      career = 'C'
      shifts = ['M', 'V']
      semesters = ['5', '6']

      expected_regex =  r'^[5|6][C][M|V][5|6][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)

    def test_n_semester_one_shifts(self):
      levels = ['5', '4', '6', '8']
      career = 'C'
      shifts = ['M']
      semesters = ['5', '4', '6', '8']

      expected_regex =  r'^[5|4|6|8][C][M][5|4|6|8][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)

    def test_n_semester_two_shifts(self):
      levels = ['5', '4', '6', '8']
      career = 'C'
      shifts = ['M', 'V']
      semesters = ['5', '4', '6', '8']

      expected_regex =  r'^[5|4|6|8][C][M|V][5|4|6|8][0-9]+$'
      self.assertEqual(generate_regex(levels, career, shifts, semesters), expected_regex)
      
class TestGetUrlForTeacher(unittest.TestCase):

  @patch('utils.text.clean_name', return_value='JOHN DOE')
  def test_get_url_for_teacher(self, mock_clean_name):
    teacher = 'John Doe'
    expected_url = 'https://foroupiicsa.net/diccionario/buscar/JOHN+DOE'
    self.assertEqual(get_url_for_teacher(teacher), expected_url)
    



