from bson import ObjectId
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class PyObjectId(ObjectId):
  @classmethod
  def __get_validators__(cls):
    yield cls.validate

  @classmethod
  def validate(cls, v):
    if not ObjectId.is_valid(v):
      raise ValueError("Invalid objectid")
    return ObjectId(v)

  @classmethod
  def __modify_schema__(cls, field_schema):
    field_schema.update(type="string")

class Comment(BaseModel):
  subject: str = Field(title="Nombre de la asignatura")
  text: str = Field(title="Comentario")
  date: str = Field(title="Fecha de publicación")
  likes: int = Field(title="Número de likes", ge=0)
  dislikes: int = Field(title='Número de dislikes', ge=0)
  positive_score: Optional[float] = Field(title="Puntuación positiva", description="Sentimiento positivo percibido en el comentario por el sistema.")
  neutral_score: Optional[float] = Field(title="Puntuación neutra", description="Sentimiento neutro percibido en el comentario por el sistema.")
  negative_score: Optional[float] = Field(title="Puntuación negativa", description="Sentimiento negativo percibido en el comentario por el sistema.")
  

class Teacher(BaseModel):
  _id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
  name: str = Field(title="Nombre del profesor")
  url: HttpUrl = Field(title="Perfil del profesor", description="Url a (diccionario de maestros) de donde se extrajeron los datos")
  positive_score: float = Field(title="Puntuación positiva", description="Opinion promedio a 3 desviaciones estándar en el diccionario de profesores")
  comments: List[Comment] = Field(title="Comentarios", description="Comentarios extraídos del diccionario de maestros.")
  
  class Config:
    allow_population_by_field_name = True
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    schema_extra = {
      "example": {
          "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
          "name": "José Pérez",
          "comments": [{
            "text": "Este es un buen profesor.",
            "date": "21-11-2019",
            "likes": 5,
            "dislikes": 0,
            "positive_score": 0.5,
            "neutral_score": 0.3,
            "negative_score": 0.2
          }],
          "positive_score": 0.22
        }
    }