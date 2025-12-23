# main.py
from fastapi import FastAPI
from routers import auth

app = FastAPI(title="API Colegio")
app.include_router(auth.router)
