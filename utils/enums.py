from enum import Enum

class Tags(str, Enum):
  courses = 'Courses'
  schedules = 'Schedules'
  teachers = 'Teachers'
  captcha = 'Captcha'
  login = 'Login'