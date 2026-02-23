from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from configuration import get_session, get_current_user
from models.publicacion import Publicacion
from models.curso_profesor import CursoProfesor
from models.curso import Curso
from models.usuario import Usuario
from models.materia import Materia
from models.enums import PerfilUsuario
from schemas.publicacion import PublicacionCreate, PublicacionOut

router = APIRouter(prefix="/publicaciones", tags=["Publicaciones"])

# Solo los profesores pueden crear publicaciones
@router.post("/cursos/{curso_id}/materias/{materia_id}/publicaciones", response_model=PublicacionOut)
def crear_publicacion(curso_id: UUID, materia_id: UUID, data: PublicacionCreate, 
                        user=Depends(get_current_user), session: Session = Depends(get_session)):
    try:

        #  Validar usuario en base
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no registrado")

        if usuario.perfil != PerfilUsuario.profesor:
            raise HTTPException(status_code=403, detail="Solo profesores pueden publicar")
        
        profesor_id = usuario.id

        #  Validar que el curso exista
        curso = session.get(Curso, curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")

        if not curso.activo:
            raise HTTPException(status_code=403, detail="El curso no está activo")
        
        #  Validar que la materia exista
        materia = session.get(Materia, materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")

        if not materia.activa:
            raise HTTPException(status_code=403, detail="La materia no está activa")
    
        #  Validar relación profesor-curso-materia
        relacion = session.exec(select(CursoProfesor).where(CursoProfesor.curso_id == curso_id,
                                        CursoProfesor.materia_id == materia_id,
                                        CursoProfesor.profesor_id == profesor_id)).first()

        if not relacion:
            raise HTTPException(status_code=403, detail="No tiene permiso para publicar en esta materia")
        
        #  Crear publicación
        nueva_publicacion = Publicacion(curso_id=curso_id, materia_id=materia_id,
                                        profesor_id=profesor_id,activa=True,**data.model_dump())

        session.add(nueva_publicacion)
        session.commit()
        session.refresh(nueva_publicacion)

    except HTTPException as e:
        raise e

    return nueva_publicacion