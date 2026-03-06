from fastapi import APIRouter, Depends, HTTPException
from services.configuration import get_session,supabase_admin,require_role
from sqlmodel import Session
from uuid import UUID
from models.curso import Curso
from models.enums import PerfilUsuario
from schemas.curso import CursoCreate, CursoOut, CursoUpdate
from datetime import datetime
router = APIRouter(prefix="/cursos", tags=["Cursos"])

@router.get("/", response_model=list[CursoOut])
def get_cursos(session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> list[CursoOut]:
    """
    Endpoint para obtener todos los cursos registrados en el sistema.

    Requiere que el usuario autenticado tenga rol de administrador.

    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role, que asegura que tenga rol de administrador.

    Retorna una lista de objetos **CursoOut** con la información de cada curso registrado,
    incluyendo nombre, turno, nivel, estado activo y fechas de creación y modificación.
    """
    cursos = session.query(Curso).all()
    respuesta = []
    for curso in cursos:
        respuesta.append(CursoOut(id=curso.id, nombre=curso.nombre, turno=curso.turno, activo=curso.activo,
                                    nivel=curso.nivel, fecha_creacion=curso.fecha_creacion,
                                    fecha_modificacion=curso.fecha_modificacion))
    return respuesta

@router.get("/{curso_id}", response_model=CursoOut)
def get_curso(curso_id: UUID, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> CursoOut:
    """
    Endpoint para obtener un curso específico a partir de su ID.

    Requiere autenticación y rol de administrador.

    - **curso_id**: Identificador único del curso que se desea consultar.
    - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **CursoOut** con los datos del curso solicitado.

    Si el curso no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
    """
    try:
        curso = session.get(Curso, curso_id)
        if not curso:
            raise HTTPException(404, "Curso no encontrada")
        return CursoOut(id=curso.id, nombre=curso.nombre, turno=curso.turno, activo=curso.activo,
                            nivel=curso.nivel, fecha_creacion=curso.fecha_creacion,
                            fecha_modificacion=curso.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener curso: {str(e)}")

@router.post("/", response_model=CursoOut)
def create_curso(curso_data: CursoCreate, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> CursoOut:
    """
    Endpoint para crear un nuevo curso en el sistema.

    Requiere autenticación y rol de administrador.

    - **curso_data**: Objeto del esquema CursoCreate que contiene los datos necesarios
      para crear el curso (nombre, turno y nivel).
    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **CursoOut** con la información del curso creado,
    incluyendo su ID generado automáticamente y sus fechas de creación y modificación.

    Si ocurre un error inesperado durante la creación, se lanza una excepción HTTP 500.
    """
    try:
        nuevo_curso = Curso(nombre=curso_data.nombre, turno=curso_data.turno, nivel=curso_data.nivel)
        session.add(nuevo_curso)
        session.commit()
        session.refresh(nuevo_curso)
        return CursoOut(id=nuevo_curso.id, nombre=nuevo_curso.nombre, turno=nuevo_curso.turno, activo=nuevo_curso.activo,
                            nivel=nuevo_curso.nivel, fecha_creacion=nuevo_curso.fecha_creacion,
                            fecha_modificacion=nuevo_curso.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear curso: {str(e)}")    

@router.put("/{curso_id}", response_model=CursoOut)
def update_curso(curso_id: UUID, curso_data: CursoUpdate, session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))) -> CursoOut:
    """
    Endpoint para actualizar un curso existente.

    Requiere autenticación y rol de administrador.

    - **curso_id**: ID del curso que se desea actualizar.
    - **curso_data**: Objeto del esquema CursoUpdate que contiene los nuevos valores
      para los campos del curso (nombre, turno, nivel y estado activo).
    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **CursoOut** con los datos actualizados del curso.

    Si el curso no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado durante la actualización, lanza una excepción HTTP 500.
    """
    try:
        curso = session.get(Curso, curso_id)
        if not curso:
            raise HTTPException(404, "Curso no encontrado")
        curso.nombre = curso_data.nombre
        curso.turno = curso_data.turno
        curso.nivel = curso_data.nivel
        curso.activo = curso_data.activo
        curso.fecha_modificacion = datetime.utcnow()
        session.add(curso)
        session.commit()
        session.refresh(curso)
        return CursoOut(id=curso.id, nombre=curso.nombre, turno=curso.turno, activo=curso.activo,
                            nivel=curso.nivel, fecha_creacion=curso.fecha_creacion,
                            fecha_modificacion=curso.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar curso: {str(e)}")

@router.delete("/{curso_id}")
def delete_curso(curso_id: UUID, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Endpoint para eliminar un curso del sistema.

    Requiere autenticación y rol de administrador.

    - **curso_id**: Identificador único del curso que se desea eliminar.
    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Si el curso existe, se elimina de la base de datos y se devuelve un mensaje de confirmación.

    Si el curso no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado durante la eliminación, lanza una excepción HTTP 500.
    """
    try:
        curso = session.get(Curso, curso_id)
        if not curso:
            raise HTTPException(404, "Curso no encontrada")
        session.delete(curso)
        session.commit()
        return {"detail": "Curso eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar curso: {str(e)}")
    

