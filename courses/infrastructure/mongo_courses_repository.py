import os

from pymongo import MongoClient
from typing import TypedDict, List

from courses.domain.model.course import Course
from courses.domain.ports.courses_repository import CourseRepository

from utils.text import generate_regex

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class MongoCourseRepository(CourseRepository):
  def connect(self) -> None:
    self.mongo_client = MongoClient(os.environ['MONGODB_CONNECTION_STRING'])
    self.database = self.mongo_client[os.environ['MONGODB_DATABASE']]
    self.course_collection = self.database['courses']

  def get_courses(
      self,
      levels: List[str],
      career: str,
      semesters: List[str],
      subjects: List[str] = [],
      shifts: List[str] = ['M', 'V']
    ) -> List[Course]:
    expression = generate_regex(levels, career, shifts, semesters)
    query = {
      "sequence": {
        "$regex": expression,
        "$options": 'i'
      }
    }
    
    if subjects:
      query['subject'] = {
        "$in": subjects
      }
    

    filtered_courses = self.course_collection.find(query)
    courses = [Course(**course) for course in filtered_courses]
    
    return courses

  
  def disconnect(self) -> None:
    self.mongo_client.close()
    