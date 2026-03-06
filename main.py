# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa la clase FastAPI para crear la aplicación y 
                                                    # CORSMiddleware para manejar las políticas de CORS 
                                                    # (Cross-Origin Resource Sharing)
from routers import auth,alumnos,profesores,publicaciones,materias,cursos,materias_curso # import los routers que usamos

app = FastAPI(title="API Colegio") # Título de la API para documentación automática con Swagger UI
#CORSMiddleware se utiliza para permitir solicitudes desde diferentes orígenes (dominios) a la API, 
# lo cual es esencial para el desarrollo frontend y pruebas. En este caso, se permiten solicitudes desde 
# "http://localhost:5500" y cualquier otro origen ("*") para facilitar las pruebas.
origins = [
    "http://localhost:5500",  # frontend local
    "*",                      # para pruebas, eñ * permite cualquier origen, pero en producción se recomienda restringirlo a los dominios específicos que necesiten acceder a la API
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, 
                                    allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router) #  Incluye las rutas definidas en el router de autenticación (auth.py)
app.include_router(alumnos.router) # Incluye las rutas definidas en el router de alumnos (alumno.py)
app.include_router(profesores.router) # Incluye las rutas definidas en el router de profesores (profesor.py)
app.include_router(publicaciones.router) # Incluye las rutas definidas en el router de publicaciones (publicaciones.py)
app.include_router(materias.router) # Incluye las rutas definidas en el router de materias (materias.py)
app.include_router(cursos.router) # Incluye las rutas definidas en el router de cursos (cursos.py)
app.include_router(materias_curso.router) # Incluye las rutas definidas en el router de materias_curso (materias_curso.py)