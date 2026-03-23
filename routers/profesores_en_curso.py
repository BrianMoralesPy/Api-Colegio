from fastapi import APIRouter, Depends  # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from schemas.profesor import ProfesorEnCursoMateriaCreate,ProfesorCursoMateriaOutFull,ProfesorEnCursoMateriaBasic
from models.enums import PerfilUsuario
from services.curso_profesor_service import CursoProfesorService
from uuid import UUID

router = APIRouter(prefix="/profesores_en_curso", tags=["ProfesoresEnCurso"])

@router.get("/", response_model=list[ProfesorCursoMateriaOutFull])
def get_profesor_en_curso_materia(materia_curso_id: UUID | None = None,
                                session: Session = Depends(get_session),
                                user=Depends(require_role(PerfilUsuario.admin))):
    profesor_en_curso_service = CursoProfesorService(session)
    return profesor_en_curso_service.get_all(materia_curso_id)


@router.post("/", response_model=ProfesorEnCursoMateriaBasic)
def asignar_curso_y_materia_a_profesor(data: ProfesorEnCursoMateriaCreate,
                                        session: Session = Depends(get_session),
                                        user=Depends(require_role(PerfilUsuario.admin))):
    profesor_en_curso_service = CursoProfesorService(session)
    return profesor_en_curso_service.assign(data)


@router.delete("/{curso_profesor_id}")
def delete_profesor_de_curso_materia(curso_profesor_id: UUID,
                                    session: Session = Depends(get_session),
                                    user=Depends(require_role(PerfilUsuario.admin))):
    profesor_en_curso_service = CursoProfesorService(session)
    return profesor_en_curso_service.delete(curso_profesor_id)