from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from uuid import uuid4
from services.configuration import upload_file_to_storage
import os

from services.configuration import get_session, get_current_user
from models.publicacion import Publicacion
from models.curso_profesor import CursoProfesor
from models.curso_alumno import CursoAlumno
from models.materia_curso import MateriaCurso
from models.archivo import Archivo
from models.usuario import Usuario
from models.enums import PerfilUsuario, TipoPublicacion
from schemas.publicacion import PublicacionCreate, PublicacionOut, PublicacionUpdate
from schemas.archivo import ArchivoOut

router = APIRouter(prefix="/publicaciones", tags=["Publicaciones"])

@router.get("/{publicacion_id}" , response_model=PublicacionOut)
def leer_publicacion(publicacion_id: UUID, user=Depends(get_current_user), 
                        session: Session = Depends(get_session)):
    try: 
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        # 🔹 ADMIN puede ver todo
        if usuario.perfil == PerfilUsuario.admin:
            return publicacion

        # 🔹 Si está inactiva
        if not publicacion.activa:
            if publicacion.profesor_id != usuario.id:
                raise HTTPException(403, "No tiene permiso para ver esta publicación")

        # 🔹 PROFESOR
        if usuario.perfil == PerfilUsuario.profesor:
            return publicacion

        # 🔹 ALUMNO
        materia_curso = session.get(MateriaCurso, publicacion.materia_curso_id)
        if not materia_curso:
            raise HTTPException(500, "MateriaCurso no encontrado")
        
        if usuario.perfil == PerfilUsuario.alumno:
            inscripcion = session.exec(select(CursoAlumno).where(CursoAlumno.alumno_id == usuario.id,
                                                                    CursoAlumno.curso_id == materia_curso.curso_id,
                                                                    CursoAlumno.ciclo_lectivo == materia_curso.ciclo_lectivo)).first()

            if not inscripcion:
                raise HTTPException(403,"No pertenece a este curso")

            return publicacion

        raise HTTPException(403, "No autorizado")

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(500, str(e))

@router.get("/{publicacion_id}/archivos", response_model=list[ArchivoOut])
def leer_archivos_publicacion(publicacion_id: UUID, user=Depends(get_current_user),
                                session: Session = Depends(get_session)):
    try:
        # 1️⃣ Validar usuario
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no registrado")

        # 2️⃣ Validar publicación
        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        # 3️⃣ Validar acceso según perfil
        if usuario.perfil == PerfilUsuario.profesor:

            relacion = session.exec(select(CursoProfesor).where(CursoProfesor.materia_curso_id == publicacion.materia_curso_id,
                                                                CursoProfesor.profesor_id == usuario.id)).first()
            if not relacion:
                raise HTTPException(403, "No tiene acceso a esta materia")

        elif usuario.perfil == PerfilUsuario.alumno:

            relacion = session.exec(select(CursoAlumno).join(MateriaCurso, CursoAlumno.curso_id == MateriaCurso.curso_id)
                                    .where(MateriaCurso.id == publicacion.materia_curso_id,CursoAlumno.alumno_id == usuario.id)
                                                                                                                        ).first()
            if not relacion:
                raise HTTPException(403, "No tiene acceso a esta materia")

        else:
            raise HTTPException(403, "Perfil no autorizado")

        # 4️⃣ Traer archivos
        archivos = session.exec(
            select(Archivo).where(
                Archivo.publicacion_id == publicacion_id
            )
        ).all()

        return archivos

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Error al obtener archivos")


@router.post("/materia-curso/{materia_curso_id}", response_model=PublicacionOut)
def crear_publicacion( materia_curso_id: UUID, data: PublicacionCreate, user=Depends(get_current_user), 
                        session: Session = Depends(get_session)):
    try:
        # 1️⃣ Validar usuario
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no registrado")

        if usuario.perfil != PerfilUsuario.profesor:
            raise HTTPException(403, "Solo profesores pueden publicar")

        profesor_id = usuario.id

        # 2️⃣ Validar que exista la materia_curso
        materia_curso = session.get(MateriaCurso, materia_curso_id)
        if not materia_curso:
            raise HTTPException(404, "Materia del curso no encontrada")

        # 3️⃣ Validar que el profesor esté asignado a esa materia_curso
        relacion = session.exec(
            select(CursoProfesor).where(CursoProfesor.materia_curso_id == materia_curso_id,
                                            CursoProfesor.profesor_id == profesor_id)).first()

        if not relacion:
            raise HTTPException(403, "No tiene permiso para publicar en esta materia")

        # 4️⃣ Crear publicación
        nueva_publicacion = Publicacion(materia_curso_id=materia_curso_id, profesor_id=profesor_id,
                                        activa=True, fecha_publicacion=datetime.utcnow(),
                                        **data.model_dump())

        session.add(nueva_publicacion)
        session.commit()
        session.refresh(nueva_publicacion)

        return nueva_publicacion

    except HTTPException:
        raise

    except Exception:
        session.rollback()
        raise HTTPException(500, "Error al crear la publicación")

@router.post("/{publicacion_id}/archivos")
def subir_archivo_publicacion(publicacion_id: UUID, file: UploadFile = File(...),
                                user=Depends(get_current_user), session: Session = Depends(get_session),):
    try:
        # 1️⃣ Validar usuario
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no registrado")

        if usuario.perfil != PerfilUsuario.profesor:
            raise HTTPException(403, "Solo profesores pueden subir archivos")

        profesor_id = usuario.id

        # 2️⃣ Validar que exista la publicación
        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")
        
        if publicacion.tipo == TipoPublicacion.aviso:
            raise HTTPException(400, "Solo las tareas o material pueden tener archivos adjuntos")


        # 3️⃣ Validar que el profesor esté asignado a esa materia_curso
        relacion = session.exec(select(CursoProfesor).where(CursoProfesor.materia_curso_id == publicacion.materia_curso_id,
                                                            CursoProfesor.profesor_id == profesor_id)).first()

        if not relacion:
            raise HTTPException(403, "No tiene permiso para subir archivos en esta materia")
        
        # 4️⃣ Generar nombre único
        extension = os.path.splitext(file.filename)[1]
        nombre_storage = f"{uuid4()}{extension}"
        ruta_storage = f"publicaciones/{publicacion_id}/{nombre_storage}"

        # 5️⃣ Subir a Supabase Storage
        upload_file_to_storage(ruta_storage, file)

        # 6️⃣ Guardar metadata en DB
        nuevo_archivo = Archivo(publicacion_id=publicacion_id, nombre_original=file.filename, ruta_archivo=ruta_storage,
                                tipo_mime=file.content_type, tamanio_bytes=file.size or 0, fecha_subida=datetime.utcnow())

        session.add(nuevo_archivo)
        session.commit()
        session.refresh(nuevo_archivo)

        return nuevo_archivo

    except HTTPException:
        raise # Re lanzar la excepción para que FastAPI la maneje

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{publicacion_id}", response_model=PublicacionUpdate)
def actualizar_publicacion(publicacion_id: UUID, data: PublicacionCreate, user=Depends(get_current_user), 
                            session: Session = Depends(get_session)):
    try:
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        if usuario.perfil != PerfilUsuario.profesor:
            raise HTTPException(403, "Solo profesores pueden modificar")

        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion or not publicacion.activa:
            raise HTTPException(404, "Publicación no encontrada")

        if publicacion.profesor_id != usuario.id:
            raise HTTPException(403, "No puede modificar esta publicación")

        # actualizar campos
        for key, value in data.model_dump(exclude_unset=True).items():  # el exclude_unset hace que este router funcione 
                                                                        # como un patch y puedas modificar algunos datos y otros no
            setattr(publicacion, key, value)

        session.add(publicacion)
        session.commit()
        session.refresh(publicacion)

        return publicacion

    except HTTPException:
        raise
    except Exception:
        session.rollback()
        raise HTTPException(500, "Error al actualizar publicacion")

@router.delete("/{publicacion_id}")
def eliminar_publicacion(publicacion_id: UUID, user=Depends(get_current_user), 
                            session: Session = Depends(get_session)):
    try:
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        # 🔹 ADMIN → Hard delete
        if usuario.perfil == PerfilUsuario.admin:
            session.delete(publicacion)
            session.commit()
            return {"detail": "Publicación eliminada definitivamente"}

        # 🔹 PROFESOR → Soft delete
        if usuario.perfil == PerfilUsuario.profesor:
            if publicacion.profesor_id != usuario.id:
                raise HTTPException(403, "No puede eliminar esta publicación")

            publicacion.activa = False
            session.add(publicacion)
            session.commit()
            return {"detail": "Publicación desactivada correctamente"}

        raise HTTPException(403, "No autorizado")

    except HTTPException:
        raise

    except Exception:
        session.rollback()
        raise HTTPException(500, "Error al eliminar la publicación")


