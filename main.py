# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa la clase FastAPI para crear la aplicación y 
                                                    # CORSMiddleware para manejar las políticas de CORS 
                                                    # (Cross-Origin Resource Sharing)
from routers import auth,alumnos,profesores # Importa los routers de autenticación, alumnos y profesores desde 
                                            # la carpeta routers

app = FastAPI(title="API Colegio") # Título de la API para documentación automática con Swagger UI
#CORSMiddleware se utiliza para permitir solicitudes desde diferentes orígenes (dominios) a la API, 
# lo cual es esencial para el desarrollo frontend y pruebas. En este caso, se permiten solicitudes desde 
# "http://localhost:5500" y cualquier otro origen ("*") para facilitar las pruebas.
origins = [
    "http://localhost:5500",  # frontend local
    "*",                      # para pruebas
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, 
                                    allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router) #  Incluye las rutas definidas en el router de autenticación (auth.py)
app.include_router(alumnos.router) # Incluye las rutas definidas en el router de alumnos (alumno.py)
app.include_router(profesores.router) # Incluye las rutas definidas en el router de profesores (profesor.py)