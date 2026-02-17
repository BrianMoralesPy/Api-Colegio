# main.py
from fastapi import FastAPI
from routers import auth,alumnos,profesores # Importa los routers de autenticación, alumnos y profesores desde la carpeta routers

app = FastAPI(title="API Colegio") # Título de la API para documentación automática con Swagger UI
app.include_router(auth.router) #  Incluye las rutas definidas en el router de autenticación (auth.py)
app.include_router(alumnos.router) # Incluye las rutas definidas en el router de alumnos (alumno.py)
app.include_router(profesores.router) # Incluye las rutas definidas en el router de profesores (profesor.py)
