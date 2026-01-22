from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from core.database import get_session
from models.profesor import Profesor
from models.usuario import Usuario
from models.enums import TiposContrato
from schemas.profesor import ProfesorUpdate, ProfesorOutFull

router = APIRouter(prefix="/profesores", tags=["Profesores"])

@router.get("/", response_model=list[ProfesorOutFull])
def get_profesores(session: Session = Depends(get_session)):
    profesores = session.query(Profesor).all()
    response = []

    for profesor in profesores:
        usuario = session.get(Usuario, profesor.id)
        if not usuario:
            continue

        response.append(
            ProfesorOutFull(
                id=profesor.id,
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                edad=usuario.edad,
                perfil=usuario.perfil,
                fecha_contratacion=profesor.fecha_contratacion,
                titulo=profesor.titulo,
                especialidad=profesor.especialidad,
                legajo=profesor.legajo,
                tipo_contrato=profesor.tipo_contrato,
                activo=profesor.activo
            )
        )
    return response


@router.get("/{profesor_id}", response_model=ProfesorOutFull)
def get_profesor(profesor_id: UUID,session: Session = Depends(get_session),):
    profesor = session.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(404, "Alumno no encontrado")

    usuario = session.get(Usuario, profesor.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")

    return ProfesorOutFull(
        id=profesor.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        edad=usuario.edad,
        perfil=usuario.perfil,
        fecha_contratacion=profesor.fecha_contratacion,
        titulo=profesor.titulo,
        especialidad=profesor.especialidad,
        legajo=profesor.legajo,
        tipo_contrato=profesor.tipo_contrato,
        activo=profesor.activo
    )


