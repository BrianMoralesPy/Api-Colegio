from fastapi import APIRouter, Depends
from core.database import get_session
from core.security.permissions import require_role
from sqlmodel import Session
from uuid import UUID
from models.enums import PerfilUsuario
from schemas.materia_curso import MateriaCursoCreate, MateriaCursoOutFull, MateriaCursoOutStandar
from services.materia_curso_service import MateriaCursoService

router = APIRouter(prefix="/materias_curso", tags=["MateriasCurso"])

@router.post("/", response_model=MateriaCursoOutStandar)
def create_materia_curso(data: MateriaCursoCreate,session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))):
    materia_curso_service = MateriaCursoService(session)
    return materia_curso_service.create(data)


@router.get("/", response_model=list[MateriaCursoOutFull])
def get_materias_curso(curso_id: UUID | None = None,ciclo_lectivo: int | None = None,
                      session: Session = Depends(get_session),user=Depends(require_role(PerfilUsuario.admin))):
    materia_curso_service = MateriaCursoService(session)
    return materia_curso_service.get_all(curso_id, ciclo_lectivo)


@router.delete("/{materia_curso_id}")
def delete_materia_curso(
    materia_curso_id: UUID,
    session: Session = Depends(get_session),
    user=Depends(require_role(PerfilUsuario.admin))
):
    materia_curso_service = MateriaCursoService(session)
    materia_curso_service.delete(materia_curso_id)
    return {"message": "MateriaCurso eliminada correctamente"}