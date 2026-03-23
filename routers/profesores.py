from fastapi import APIRouter, Depends# Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session #  Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from schemas.profesor import ProfesorFullUpdate
from models.enums import PerfilUsuario
from services.profesor_service import ProfesorService
from uuid import UUID

router = APIRouter(prefix="/profesores", tags=["Profesores"])   # Crea un router de FastAPI con el prefijo "/profesores" 
                                                                # para agrupar las rutas relacionadas con los profesores y 
                                                                # asigna la etiqueta "Profesores" para la documentación automática
@router.get("/")
def obtener_profesores(session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    profesor_service = ProfesorService(session)
    return profesor_service.get_profesores()

@router.get("/{profesor_id}")
def obtener_profesor(profesor_id:UUID, session:Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    profesor_service = ProfesorService(session)
    return profesor_service.get_profesor(profesor_id)

@router.put("/{profesor_id}")
def actualizar_profesor(profesor_id:UUID, data:ProfesorFullUpdate,
                        session:Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))):
    profesor_service = ProfesorService(session)
    return profesor_service.update_profesor(profesor_id, data.profesor, data.usuario)

@router.delete("/{profesor_id}")
def eliminar_profesor(profesor_id: UUID,session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))):
    profesor_service = ProfesorService(session)
    return profesor_service.delete_profesor(profesor_id) 
