from fastapi import APIRouter, Depends # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from models.enums import PerfilUsuario
from schemas.materia import MateriaUpdate,MateriaCreate
from services.materia_service import MateriaService
from uuid import UUID 

router = APIRouter(prefix="/materias", tags=["Materias"]) # Crea un router de FastAPI con el prefijo "/materias" para agrupar 
                                                        # las rutas relacionadas con los materias y asigna la etiqueta "Materias" 
                                                        # para la documentación automática
@router.get("/")
def obtener_materias(session: Session = Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))):
    materia_service = MateriaService(session)
    return materia_service.get_materias()

@router.get("/{materia_id}")
def obtener_materia(materia_id: UUID,session: Session = Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))):
    materia_service = MateriaService(session)
    return materia_service.get_materia(materia_id)

@router.post("/")
def crear_materia(data: MateriaCreate,session: Session = Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))):
    materia_service = MateriaService(session)
    return materia_service.create_materia(data)

@router.put("/{materia_id}")
def actualizar_materia(materia_id: UUID, data: MateriaUpdate,session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))):
    materia_service = MateriaService(session)
    return materia_service.update_materia(materia_id,data)

@router.delete("/{materia_id}")
def eliminar_materia(materia_id: UUID,session: Session = Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))):
    materia_service = MateriaService(session)
    return materia_service.delete_materia(materia_id) 