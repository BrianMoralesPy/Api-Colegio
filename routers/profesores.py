from fastapi import APIRouter, Depends, HTTPException # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session #  Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from services.configuration import get_session,supabase_admin  # Importa la función get_session para obtener una sesión de base de datos y 
                                                # la instancia de Supabase desde el archivo de configuración 
from uuid import UUID
from models.profesor import Profesor
from models.usuario import Usuario
from schemas.profesor import ProfesorUpdate, ProfesorOutFull
from schemas.usuario import UsuarioUpdate
from models.historial_contrasenas import HistorialContrasenas

router = APIRouter(prefix="/profesores", tags=["Profesores"])   # Crea un router de FastAPI con el prefijo "/profesores" 
                                                                # para agrupar las rutas relacionadas con los profesores y 
                                                                # asigna la etiqueta "Profesores" para la documentación automática

@router.get("/", response_model=list[ProfesorOutFull])
def get_profesores(session: Session = Depends(get_session)) -> list[ProfesorOutFull]:
    profesores = session.query(Profesor).all()
    respuesta = []

    for profesor in profesores:
        usuario = session.get(Usuario, profesor.id)
        if not usuario:
            continue

        respuesta.append(
            ProfesorOutFull(id=profesor.id, nombre=usuario.nombre, apellido=usuario.apellido, edad=usuario.edad,
                            perfil=usuario.perfil, ruta_foto = usuario.ruta_foto, fecha_contratacion=profesor.fecha_contratacion,
                            titulo=profesor.titulo, especialidad=profesor.especialidad, legajo=profesor.legajo,
                            tipo_contrato=profesor.tipo_contrato, activo=profesor.activo))
    return respuesta

@router.get("/{profesor_id}", response_model=ProfesorOutFull)
def get_profesor(profesor_id: UUID, session: Session = Depends(get_session)) -> ProfesorOutFull:
    profesor = session.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(404, "Profesor no encontrado")

    usuario = session.get(Usuario, profesor.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")

    return ProfesorOutFull(id=profesor.id, nombre=usuario.nombre, apellido=usuario.apellido, edad=usuario.edad,
                            perfil=usuario.perfil, ruta_foto=usuario.ruta_foto, fecha_contratacion=profesor.fecha_contratacion,
                            titulo=profesor.titulo, especialidad=profesor.especialidad, legajo=profesor.legajo,
                            tipo_contrato=profesor.tipo_contrato, activo=profesor.activo)

@router.put("/{profesor_id}")
def update_profesor(profesor_id:UUID, profesor_data:ProfesorUpdate, usuario_data:UsuarioUpdate, 
                    session:Session=Depends(get_session)) -> dict:
    profesor = session.get(Profesor, profesor_id)
    if not profesor:
        raise HTTPException(404, "Profesor no encontrado")
    
    usuario = session.get(Usuario, profesor.id)
    if not usuario:
        raise HTTPException(500, "Usuario inconsistente")
    
    #Actualizar Profesor
    for key, value in profesor_data.model_dump(exclude_unset=True).items():
        setattr(profesor, key, value)
    #Actualizar Usuario
    for key, value in usuario_data.model_dump(exclude_unset=True).items():
        setattr(usuario, key, value)
    
    session.commit()
    session.refresh(profesor)
    session.refresh(usuario)
    
    return {"detail":"Profesor actualizado correctamente"}

@router.delete("/{profesor_id}")
def delete_profesor(profesor_id: UUID,session: Session = Depends(get_session)) -> dict:
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
        supabase_admin.auth.admin.delete_user(str(usuario.id))

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar profesor: {str(e)}")

    return {"detail": "Profesor eliminado definitivamente"}
