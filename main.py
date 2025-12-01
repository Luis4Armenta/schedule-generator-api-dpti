import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from routes.schedule import router as schedule_router
from routes.captcha import router as captcha_router
from routes.login import router as login_router
from courses.domain.ports.courses_repository import CourseRepository
from courses.infrastructure.mongo_courses_repository import MongoCourseRepository

from utils.enums import Tags

app = FastAPI()
app.title = 'Profesores-API'
app.version = '0.0.1'

@app.on_event('startup')
def startup_db_clients():

  app.courses = MongoCourseRepository()
  
  app.courses.connect()
  
  schedule_router.courses = app.courses  
  

origins = ["*"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(schedule_router, tags=[Tags.schedules])
app.include_router(captcha_router, tags=[Tags.captcha])
app.include_router(login_router, tags=[Tags.login])



@app.get('/', tags=['home'])
def message() -> HTMLResponse:
  return HTMLResponse('<h1>Profesores API</h1>')



@app.on_event('shutdown')
def shutdown_db_clients():
  app.courses.disconnect()
