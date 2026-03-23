from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session
from uuid import UUID
from core.security.permissions import get_current_user
from core.database import get_session
from schemas.publicacion import PublicacionCreate, PublicacionOut, PublicacionUpdate
from schemas.archivo_publicacion import ArchivoPublicacionOut
from schemas.entregas import CorreccionCreate

from services.publicacion_service import PublicacionService

router = APIRouter(prefix="/publicaciones", tags=["Publicaciones"])

@router.get("/{publicacion_id}", response_model=PublicacionOut)
def leer_publicacion(publicacion_id: UUID,user=Depends(get_current_user),
                    session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.leer_publicacion(publicacion_id, user["sub"])

@router.get("/archivos_publicacion/{publicacion_id}", response_model=list[ArchivoPublicacionOut])
def leer_archivos(publicacion_id: UUID,user=Depends(get_current_user),
                session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.leer_archivos(publicacion_id, user["sub"])

@router.post("/{materia_curso_id}", response_model=PublicacionOut)
def crear_publicacion(materia_curso_id: UUID, data: PublicacionCreate, user=Depends(get_current_user),
                    session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.crear_publicacion(materia_curso_id, data, user["sub"])

@router.post("/subir_archivo/{publicacion_id}", response_model=ArchivoPublicacionOut)
def subir_archivo(publicacion_id: UUID, file: UploadFile = File(...), 
                user=Depends(get_current_user),session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.subir_archivo(publicacion_id, file, user["sub"])

@router.post("/subir_tarea_entregada/{publicacion_id}")
def subir_tarea_entregada(publicacion_id: UUID, file: UploadFile = File(...), 
                user=Depends(get_current_user),session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.entregar_tarea(publicacion_id, file, user["sub"])

@router.put("/correcion_tarea/{publicacion_id}")
def corregir_tarea(publicacion_id:UUID, data:CorreccionCreate, 
                    user=Depends(get_current_user),session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.corregir_entrega(publicacion_id, data, user["sub"])

@router.put("/{publicacion_id}", response_model=PublicacionOut)
def actualizar_publicacion(publicacion_id: UUID, data: PublicacionUpdate, user=Depends(get_current_user),
                        session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.actualizar_publicacion(publicacion_id, data, user["sub"])

@router.delete("/{publicacion_id}")
def eliminar_publicacion(publicacion_id: UUID, user=Depends(get_current_user),
                        session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.eliminar_publicacion(publicacion_id, user["sub"])

@router.get("/descargar_archivo/{archivo_id}")
def descargar_archivo(archivo_id: UUID,user=Depends(get_current_user),
                        session: Session = Depends(get_session)):
    publicacion_service = PublicacionService(session)
    return publicacion_service.descargar_archivo(archivo_id, user["sub"])