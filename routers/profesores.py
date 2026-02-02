from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID
from core.database import get_session
from models.profesor import Profesor
from models.usuario import Usuario
from models.enums import TiposContrato
from schemas.profesor import ProfesorUpdate, ProfesorOutFull
from schemas.usuario import UsuarioUpdate
from core.supabase import supabase
from models.historial_contrasenas import HistorialContrasenas

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
        raise HTTPException(404, "Profesor no encontrado")

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

@router.delete("/{profesor_id}")
def delete_profesor(profesor_id: UUID,session: Session = Depends(get_session),):
    profesor = session.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(404, "Profesor no encontrado")

    usuario = session.get(Usuario, profesor.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")

    try:
        session.query(HistorialContrasenas).filter(HistorialContrasenas.user_id == usuario.id).delete()
        session.delete(profesor)
        session.delete(usuario)
        session.commit()
        supabase.auth.admin.delete_user(str(usuario.id))

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar profesor: {str(e)}"
        )

    return {"detail": "Profesor eliminado definitivamente"}

@router.put("/{profesor_id}")
def update_alumno(profesor_id:UUID,profesor_data:ProfesorUpdate,usuario_data:UsuarioUpdate,session:Session=Depends(get_session),):
    profesor = session.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(404, "Profesor no encontrado")
    
    usuario = session.get(Usuario, profesor.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")
    #Actualizar Profesor
    for field, value in profesor_data.model_dump(exclude_unset=True).items():
        setattr(profesor, field, value)
    #Actualizar Usuario
    for field, value in usuario_data.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)
    
    session.commit()
    session.refresh(profesor)
    session.refresh(usuario)
    return {"detail":"Profesor actualizado correctamente"}


