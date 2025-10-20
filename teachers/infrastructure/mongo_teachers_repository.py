import os

from pymongo import MongoClient
from typing import TypedDict, Optional

from teachers.domain.model.teacher import Teacher
from teachers.domain.ports.teachers_repository import TeacherRepository

def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

@singleton
class MongoTeachersRepository(TeacherRepository):
  def connect(self) -> None:
    self.mongo_client = MongoClient(os.environ['MONGODB_CONNECTION_STRING'])
    self.database = self.mongo_client[os.environ['MONGODB_DATABASE']]
    self.teachers_collection = self.database['teachers']
    
  def get_teacher(self, teacher_name: str) -> Optional[Teacher]:
    teacher = self.teachers_collection.find_one({'name': teacher_name})

    if teacher:
      return Teacher(
        id=teacher['_id'],
        name=teacher['name'],
        url=teacher['url'],
        comments=teacher['comments'],
        positive_score=teacher['positive_score']
      )
    else:
      return None
  
  def disconnect(self) -> None:
    self.mongo_client.close()
    