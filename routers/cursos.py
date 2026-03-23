from fastapi import APIRouter, Depends # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from models.enums import PerfilUsuario
from schemas.curso import CursoCreate,CursoUpdate
from services.curso_service import CursoService
from uuid import UUID

router = APIRouter(prefix="/cursos", tags=["Cursos"]) # Crea un router de FastAPI con el prefijo "/cursos" para agrupar 
                                                        # las rutas relacionadas con los cursos y asigna la etiqueta "Cursos" 
                                                        # para la documentación automática
                                                        # user=Depends(require_role(PerfilUsuario.admin))
@router.get("/")
def obtener_cursos(session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    curso_service = CursoService(session)
    return curso_service.get_cursos()

@router.get("/{curso_id}")
def obtener_curso(curso_id: UUID,session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))) :
    curso_service = CursoService(session)
    return curso_service.get_curso(curso_id)

@router.post("/")
def crear_curso(data: CursoCreate,session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    curso_service = CursoService(session)
    return curso_service.create_curso(data)

@router.put("/{curso_id}")
def actualizar_curso(curso_id: UUID, data: CursoUpdate,session: Session = Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))):
    curso_service = CursoService(session)
    return curso_service.update_curso(curso_id,data)

@router.delete("/{curso_id}")
def eliminar_curso(curso_id: UUID,session: Session = Depends(get_session),
                user=Depends(require_role(PerfilUsuario.admin))):
    curso_service = CursoService(session)
    return curso_service.delete_curso(curso_id) 