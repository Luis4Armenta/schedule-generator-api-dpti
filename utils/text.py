import re
from unidecode import unidecode
from typing import List

def clean_name(name: str) -> str:
  # Convertir caracteres especiales a su equivalente sin acentos
  cleaned_name = unidecode(name)
  # Eliminar caracteres no alfabéticos y convertir a mayúsculas
  cleaned_name = re.sub(r'[^a-zA-Z\s]', '', cleaned_name).upper()
  # Eliminar espacios innecesarios
  cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
  # Eliminar espacios al inicio y al final de la cadena
  cleaned_name = cleaned_name.strip()
  return cleaned_name

def generate_regex(levels: List[str], career: str, shifts: List[str], semesters: List[str]):
  level_regex = '|'.join(levels)
  career_regex = re.escape(career)
  shift_regex = '|'.join(shifts)
  semester_regex = '|'.join(semesters)
  
  regex_pattern = r'^[' + level_regex + r'][' + career_regex + r'][' + shift_regex + r'][' + semester_regex + r'][0-9]+$'
  return regex_pattern

def get_url_for_teacher(teacher: str) -> str:
  parsed_name = clean_name(teacher)
  parsed_name: str = parsed_name.replace(' ', '+')
  
  url = f'https://foroupiicsa.net/diccionario/buscar/{parsed_name}'
  return url
