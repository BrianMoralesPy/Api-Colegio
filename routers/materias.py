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
    materias = session.query(Materia).all()
    respuesta = []
    for materia in materias:
        respuesta.append(MateriaOut(id=materia.id, nombre=materia.nombre,codigo=materia.codigo, descripcion=materia.descripcion,
                                    activa=materia.activa, fecha_creacion=materia.fecha_creacion,
                                    fecha_modificacion=materia.fecha_modificacion))
    return respuesta

@router.get("/{materia_id}", response_model=MateriaOut)
def get_materia(materia_id: UUID, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> MateriaOut:
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
def create_materia(materia_data: MateriaCreate, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> MateriaOut:
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
def delete_materia(materia_id: UUID, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> dict:
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
    

