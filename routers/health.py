from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text
from services.configuration import get_session
import time


router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health check del servicio") # Decorador que define la ruta y la documentación de la ruta
def health_check(session: Session = Depends(get_session)): # Dependencia que obtiene la sesión de la base de datos
    try:
        start = time.time()  # Tiempo de inicio
        session.exec(text("SELECT 1")) # Ejecutar una consulta SQL
        response_time = round((time.time() - start) * 1000, 2) # Tiempo de respuesta

        return {"status": "ok", "database": "connected", "response_time_ms": response_time} # Retornar la respuesta
    except Exception:
        raise HTTPException(status_code=503, detail="Database connection error")