from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from core.database import get_session
from models.alumno import Alumno
from models.usuario import Usuario
from models.enums import PerfilUsuario
from schemas.alumno import AlumnoUpdate,AlumnoOutFull

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])

""" def require_admin(user=Depends(get_current_user)):
    if user["perfil"] != PerfilUsuario.admin:
        raise HTTPException(
            status_code=403,
            detail="Permisos insuficientes"
        )
    return user """

@router.get("/", response_model=list[AlumnoOutFull])
def get_alumnos(session: Session = Depends(get_session)):
    alumnos = session.query(Alumno).all()
    response = []

    for alumno in alumnos:
        usuario = session.get(Usuario, alumno.id)
        if not usuario:
            continue

        response.append(
            AlumnoOutFull(
                id=alumno.id,
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                edad=usuario.edad,
                perfil=usuario.perfil,
                legajo=alumno.legajo,
                fecha_ingreso=alumno.fecha_ingreso,
                estado=alumno.estado,
                observaciones=alumno.observaciones,
                activo=alumno.activo,
            )
        )
    return response


@router.get("/{alumno_id}", response_model=AlumnoOutFull)
def get_alumno(alumno_id: UUID,session: Session = Depends(get_session),):
    alumno = session.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    usuario = session.get(Usuario, alumno.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")

    return AlumnoOutFull(
        id=alumno.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        edad=usuario.edad,
        perfil=usuario.perfil,
        legajo=alumno.legajo,
        fecha_ingreso=alumno.fecha_ingreso,
        estado=alumno.estado,
        observaciones=alumno.observaciones,
        activo=alumno.activo
    )


