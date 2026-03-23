from fastapi import APIRouter, Depends  # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from core.database import get_session
from core.security.permissions import require_role
from schemas.alumno import AlumnoEnCursoCreate,AlumnoCursoOutFull,AlumnoEnCursoBasic
from models.enums import PerfilUsuario
from services.curso_alumno_service import CursoAlumnoService

from uuid import UUID

router = APIRouter(prefix="/alumnos_en_curso", tags=["AlumnosEnCurso"])
@router.get("/", response_model=list[AlumnoCursoOutFull])
def get_alumno_en_curso(curso_id: UUID | None = None,ciclo_lectivo: int | None = None,
                        session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))):
    alumno_en_curso = CursoAlumnoService(session)
    return alumno_en_curso.get_all(curso_id, ciclo_lectivo)


@router.post("/", response_model=AlumnoEnCursoBasic)
def asignar_curso_a_alumno(data: AlumnoEnCursoCreate,session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))):
    alumno_en_curso = CursoAlumnoService(session)
    return alumno_en_curso.assign(data)

@router.delete("/{curso_alumno_id}")
def delete_alumno_de_curso(curso_alumno_id: UUID, session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))):
    alumno_en_curso = CursoAlumnoService(session)
    return alumno_en_curso.delete(curso_alumno_id)
