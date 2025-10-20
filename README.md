# Generador de horarios UPIICSA API

Se trata de una API desarrollada en FastAPI que emplea web scraping para extraer horarios del SAES (Secuencias formadas por diferentes unidades de aprendizaje, mismas que tienen un profesor asignado, con diferentes sesiones a la semana) y comentarios sobre los profesores que las imparten. El generador de horarios utiliza estos datos extraídos de la web para generar todos los posibles horarios mediante un algoritmo de backtracking y puntuarlos de acuerdo al agrado que los alumnos han manifestado en comentarios sobre los profesores que integran cada uno de los horarios.

## Características

- Extrae horarios de clase de documentos HTML exportados del SAES.
- Genera todas las posibles combinaciones de materias de acuerdo a los parámetros dados (Hora de entrada, hora de salida, límite de créditos, materias obligatorias, exclusión de profesores, etc).
- Extrae comentarios automáticamente del diccionario de maestros.
- Realiza análisis de sentimiento sobre comentarios de profesores.
- Asigna una puntuación positiva a los profesores según los comentarios que en el diccionario de maestros se hayan.
- Ordena los horarios generados según la puntuación positiva.

## Instalación
### Python y PIP
Para esta instalación debes tener instalado en tu computadora la versión 3.9 de Python junto con [Python Package Index](https://pypi.org/project/pip/) (pip).

1. Si lo deseas puedes utilizar [venv](https://docs.python.org/es/3/library/venv.html) para crear un entorno virtual aislado en el que se instalaran las dependencias del proyecto y activarlo:
`$ python -m venv /path/to/new/virtual/environment`
`$ source env/bin/activate`

2. Instala las dependencias desde requirements.txt con pip.
`$ pip install -r requirements.txt `

3. Modifica las variables del archivo `.env copy` con las credenciales y direcciones de tu base de datos MongoDB y tus servicios de Azure.

4. Puedes cambiar el nombre del archivo de `.env copy` a `.env`.

5. Una vez colocadas correctamente las variables de entorno en `.env` puedes correr el servidor con uvicorn (Puedes averiguar más sobre uvicorn en su [documentación](https://www.uvicorn.org/)).
`$ uvicorn main:app --env-file .env --port 3000 --host 0.0.0.0 --reload`

6. Listo. Puedes acceder a la documentación automática de la API mediante la ruta `http://localhost:3000/docs'.

### Docker Compose
Necesitarás tener Docker compose instalado en tu computadora.\

1. Modifica las variables del archivo `.env copy` agregando tus credenciales de Azure (Puedes dejar las variables relacionadas con MongoDB como están).

2. Cambia el nomnre del archivo `.env copy` a `.env`.
3. Haz el build con Docker Compose.
`$ docker-compose build`

4. Levanta los contenedores con Docker Compose.
`$ docker-compose up`

5. Listo. Puedes acceder a la documentación automática de la API mediante la ruta `http://localhost:3000/docs'.
