# main.py
from fastapi import FastAPI
from routers import auth,alumnos,profesores

app = FastAPI(title="API Colegio")
app.include_router(auth.router)
app.include_router(alumnos.router)
app.include_router(profesores.router)
