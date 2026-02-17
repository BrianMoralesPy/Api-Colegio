from fastapi import APIRouter, Depends, HTTPException # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from uuid import UUID 
from configuration import supabase # Importa la instancia de Supabase desde el archivo de configuración
from configuration import get_session # Importa la función get_session para obtener una sesión de base de datos
from models.alumno import Alumno
from models.usuario import Usuario
from models.historial_contrasenas import HistorialContrasenas
from schemas.usuario import UsuarioUpdate
from schemas.alumno import AlumnoUpdate,AlumnoOutFull

router = APIRouter(prefix="/alumnos", tags=["Alumnos"]) # Crea un router de FastAPI con el prefijo "/alumnos" para agrupar las rutas relacionadas con los alumnos y asigna la etiqueta "Alumnos" para la documentación automática

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
                foto_url=usuario.foto_url,
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
        foto_url=usuario.foto_url,
        legajo=alumno.legajo,
        fecha_ingreso=alumno.fecha_ingreso,
        estado=alumno.estado,
        observaciones=alumno.observaciones,
        activo=alumno.activo
    )

@router.delete("/{alumno_id}")
def delete_alumno(alumno_id: UUID,session: Session = Depends(get_session),):
    alumno = session.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    usuario = session.get(Usuario, alumno.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")

    try:
        session.query(HistorialContrasenas).filter(HistorialContrasenas.user_id == usuario.id).delete()
        session.delete(alumno)
        session.delete(usuario)
        session.commit()
        supabase.auth.admin.delete_user(str(usuario.id))

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar alumno: {str(e)}"
        )

    return {"detail": "Alumno eliminado definitivamente"}

@router.put("/{alumno_id}")
def update_alumno(alumno_id:UUID,alumno_data:AlumnoUpdate,usuario_data:UsuarioUpdate,session:Session=Depends(get_session),):
    alumno = session.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")
    
    usuario = session.get(Usuario, alumno.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")
    #Actualizar Alumno
    for key, value in alumno_data.model_dump(exclude_unset=True).items():
        setattr(alumno, key, value)
    #Actualizar Usuario
    for key, value in usuario_data.model_dump(exclude_unset=True).items():
        setattr(usuario, key, value)
    
    session.commit()
    session.refresh(alumno)
    session.refresh(usuario)
    return {"detail":"Alumno actualizado correctamente"}



