from fastapi import APIRouter, Depends  # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from schemas.alumno import AlumnoFullUpdate
from models.enums import PerfilUsuario
from services.alumno_service import AlumnoService
from uuid import UUID 

router = APIRouter(prefix="/alumnos", tags=["Alumnos"]) # Crea un router de FastAPI con el prefijo "/alumnos" para agrupar 
                                                        # las rutas relacionadas con los alumnos y asigna la etiqueta "Alumnos" 
                                                        # para la documentación automática
@router.get("/")
def obtener_alumnos(session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    alumno_service = AlumnoService(session)
    return alumno_service.get_alumnos()

@router.get("/{alumno_id}")
def obtener_alumno(alumno_id: UUID,session: Session = Depends(get_session), 
                user=Depends(require_role(PerfilUsuario.admin))):
    alumno_service = AlumnoService(session)
    return alumno_service.get_alumno(alumno_id)

@router.put("/{alumno_id}")
def actualizar_alumno(alumno_id: UUID, data: AlumnoFullUpdate,
                        session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))):
    alumno_service = AlumnoService(session)
    return alumno_service.update_alumno(alumno_id,data.alumno,data.usuario)

@router.delete("/{alumno_id}")
def eliminar_alumno(alumno_id: UUID,session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))):
    alumno_service = AlumnoService(session)
    return alumno_service.delete_alumno(alumno_id)
