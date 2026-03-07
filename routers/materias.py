from fastapi import APIRouter, Depends, HTTPException
from services.configuration import get_session,supabase_admin,require_role
from sqlmodel import Session
from uuid import UUID
from models.materia import Materia
from models.enums import PerfilUsuario
from schemas.materia import MateriaCreate, MateriaOut, MateriaUpdate
from datetime import datetime
router = APIRouter(prefix="/materias", tags=["Materias"])

@router.get("/", response_model=list[MateriaOut])
def get_materias(session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> list[MateriaOut]:
    """
    Endpoint para obtener todos las materias registrados en el sistema.

    Requiere que el usuario autenticado tenga rol de administrador.

    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role, que asegura que tenga rol de administrador.

    Retorna una lista de objetos **MateriaOut** con la información de cada materia registrada,
    incluyendo nombre, codigo, activo , descripcion , fechas de creación y modificación.
    """
    materias = session.query(Materia).all()
    respuesta = []
    for materia in materias:
        respuesta.append(MateriaOut(id=materia.id, nombre=materia.nombre,codigo=materia.codigo, descripcion=materia.descripcion,
                                    activa=materia.activa, fecha_creacion=materia.fecha_creacion,
                                    fecha_modificacion=materia.fecha_modificacion))
    return respuesta

@router.get("/{materia_id}", response_model=MateriaOut)
def get_materia(materia_id: UUID, session: Session = Depends(get_session), 
                user=Depends(require_role(PerfilUsuario.admin))) -> MateriaOut:
    """
    Endpoint para obtener una materia específica a partir de su ID.

    Requiere autenticación y rol de administrador.

    - **materia_id**: Identificador único del materia que se desea consultar.
    - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **MateriaOut** con los datos de la materia solicitado.

    Si la materia no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
    """
    try:
        materia = session.get(Materia, materia_id)
        if not materia:
            raise HTTPException(404, "Materia no encontrada")
        return MateriaOut(id=materia.id, nombre=materia.nombre, codigo=materia.codigo, descripcion=materia.descripcion,
                            activa=materia.activa, fecha_creacion=materia.fecha_creacion,
                            fecha_modificacion=materia.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener materia: {str(e)}")

@router.post("/", response_model=MateriaOut)
def create_materia(materia_data: MateriaCreate, session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))) -> MateriaOut:
    """
    Endpoint para obtener una materia específica a partir de su ID.

    Requiere autenticación y rol de administrador.

    - **materia_id**: Identificador único del materia que se desea consultar.
    - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **MateriaOut** con los datos del materia solicitado.

    Si el materia no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
    """
    try:
        nueva_materia = Materia(nombre=materia_data.nombre, codigo=materia_data.codigo, descripcion=materia_data.descripcion)
        session.add(nueva_materia)
        session.commit()
        session.refresh(nueva_materia)
        return MateriaOut(id=nueva_materia.id, nombre=nueva_materia.nombre, codigo=nueva_materia.codigo, descripcion=nueva_materia.descripcion,
                            activa=nueva_materia.activa, fecha_creacion=nueva_materia.fecha_creacion,
                            fecha_modificacion=nueva_materia.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear materia: {str(e)}")    

@router.put("/{materia_id}", response_model=MateriaOut)
def update_materia(materia_id: UUID, materia_data: MateriaUpdate, session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))) -> MateriaOut:
    """
    Endpoint para actualizar una materia existente.

    Requiere autenticación y rol de administrador.

    - **materia_id**: ID de la materia que se desea actualizar.
    - **materia_data**: Objeto del esquema MateriaUpdate que contiene los nuevos valores
      para los campos de la materia (nombre, descripcion, codigo y activo).
    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Retorna un objeto **MateriaOut** con los datos actualizados del materia.

    Si la materia no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado durante la actualización, lanza una excepción HTTP 500.
    """
    try:
        materia = session.get(Materia, materia_id)
        if not materia:
            raise HTTPException(404, "Materia no encontrada")
        materia.nombre = materia_data.nombre
        materia.codigo = materia_data.codigo
        materia.descripcion = materia_data.descripcion
        materia.activa = materia_data.activa
        materia.fecha_modificacion = datetime.utcnow()
        session.add(materia)
        session.commit()
        session.refresh(materia)
        return MateriaOut(id=materia.id, nombre=materia.nombre, codigo=materia.codigo, descripcion=materia.descripcion,
                            activa=materia.activa, fecha_creacion=materia.fecha_creacion,
                            fecha_modificacion=materia.fecha_modificacion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar materia: {str(e)}")

@router.delete("/{materia_id}")
def delete_materia(materia_id: UUID, session: Session = Depends(get_session), 
                    user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Endpoint para eliminar una materia del sistema.

    Requiere autenticación y rol de administrador.

    - **materia_id**: Identificador único de la materia que se desea eliminar.
    - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
    - **user**: Usuario autenticado validado mediante require_role.

    Si la materia existe, se elimina de la base de datos y se devuelve un mensaje de confirmación.

    Si la materia no existe, lanza una excepción HTTP 404.
    Si ocurre un error inesperado durante la eliminación, lanza una excepción HTTP 500.
    """
    try:
        materia = session.get(Materia, materia_id)
        if not materia:
            raise HTTPException(404, "Materia no encontrada")
        session.delete(materia)
        session.commit()
        return {"detail": "Materia eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar materia: {str(e)}")
    

