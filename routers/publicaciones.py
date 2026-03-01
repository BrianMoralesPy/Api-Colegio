from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime, timezone
from uuid import uuid4
from services.configuration import upload_file_to_storage
import os

from services.configuration import get_session, get_current_user, generate_signed_url
from models.publicacion import Publicacion
from models.curso_profesor import CursoProfesor
from models.curso_alumno import CursoAlumno
from models.materia_curso import MateriaCurso
from models.archivo_publicacion import ArchivosPublicacion
from models.usuario import Usuario
from models.entrega import Entrega
from models.tarea_entregada import TareaEntregada
from models.enums import PerfilUsuario, TipoPublicacion, EstadosEntregas
from schemas.publicacion import PublicacionCreate, PublicacionOut, PublicacionUpdate
from schemas.archivo_publicacion import ArchivoPublicacionOut
from schemas.entregas import CorreccionCreate

router = APIRouter(prefix="/publicaciones", tags=["Publicaciones"])

@router.get("/{publicacion_id}" , response_model=PublicacionOut)
def leer_datos_publicacion(publicacion_id: UUID, user=Depends(get_current_user), 
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

@router.get("/archivos_publicacion/{publicacion_id}", response_model=list[ArchivoPublicacionOut])
def leer_archivos_tarea_o_material_publicacion(publicacion_id: UUID, user=Depends(get_current_user),
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
        archivos = session.exec(select(ArchivosPublicacion).where(ArchivosPublicacion.publicacion_id == publicacion_id)).all()

        return archivos

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Error al obtener archivos")


@router.post("/{materia_curso_id}", response_model=PublicacionOut)
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

@router.post("/archivos/{publicacion_id}")   # se puede utilizar cuando creamos la publicacion o la actualizamos mas que nada si el profesor
def subir_material_o_tarea(publicacion_id: UUID, file: UploadFile = File(...),
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
        
        if publicacion.tipo == TipoPublicacion.tarea:
            carpeta_storage = f"tareas/{publicacion_id}"
        elif publicacion.tipo == TipoPublicacion.material:
            carpeta_storage = f"material/{publicacion_id}"

        # 4️⃣ Generar nombre único
        extension = os.path.splitext(file.filename)[1]
        nombre_storage = f"{uuid4()}{extension}"
        ruta_storage = f"{carpeta_storage}/{nombre_storage}"

        # 5️⃣ Subir a Supabase Storage
        upload_file_to_storage(ruta_storage, file)

        # 6️⃣ Guardar metadata en DB
        nuevo_archivo_publicacion = ArchivosPublicacion(publicacion_id=publicacion_id, nombre_original=file.filename, ruta_archivo=ruta_storage,
                                tipo_mime=file.content_type, tamanio_bytes=file.size or 0, fecha_subida=datetime.utcnow())

        session.add(nuevo_archivo_publicacion)
        session.commit()
        session.refresh(nuevo_archivo_publicacion)

        return nuevo_archivo_publicacion

    except HTTPException:
        raise # Re lanzar la excepción para que FastAPI la maneje

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entregar_tarea/{publicacion_id}") # subimos tarea al storage y tambien los datos a su tabla
def entregar_tarea(publicacion_id: UUID, file: UploadFile = File(...),
                    user=Depends(get_current_user),session: Session = Depends(get_session)):
    try:
        # 🔹 Obtener usuario real
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(401, "Usuario no encontrado")

        if usuario.perfil != PerfilUsuario.alumno:
            raise HTTPException(403, "Solo alumnos pueden entregar tareas")

        # 🔹 Validar publicación
        publicacion = session.get(Publicacion, publicacion_id)
        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        if publicacion.tipo != TipoPublicacion.tarea:
            raise HTTPException(400, "Solo se pueden entregar tareas")

        if publicacion.fecha_entrega and datetime.now(timezone.utc) > publicacion.fecha_entrega:
            raise HTTPException(400, "La tarea está vencida")

        # 🔹 Validar inscripción
        relacion = session.exec(select(CursoAlumno).join(MateriaCurso, CursoAlumno.curso_id == MateriaCurso.curso_id).where(
                            MateriaCurso.id == publicacion.materia_curso_id, CursoAlumno.alumno_id == usuario.id)).first()

        if not relacion:
            raise HTTPException(403, "No tiene permiso para entregar en esta materia")

        # 🔹 Crear o actualizar entrega
        entrega = session.exec(select(Entrega).where(Entrega.publicacion_id == publicacion_id, Entrega.alumno_id == usuario.id)).first()

        if not entrega:
            entrega = Entrega(publicacion_id=publicacion_id, alumno_id=usuario.id, fecha_creacion=datetime.now(timezone.utc),
                                estado=EstadosEntregas.entregado)
            session.add(entrega)
            session.commit()
            session.refresh(entrega)
        else:
            entrega.fecha_actualizacion = datetime.now(timezone.utc)
            entrega.estado = EstadosEntregas.entregado
            session.commit()

        # 🔹 Generar nombre único para storage
        extension = os.path.splitext(file.filename)[1]
        nombre_storage = f"{uuid4()}{extension}"

        ruta_storage = f"entregas/{publicacion_id}-{usuario.id}/{nombre_storage}"

        # 🔹 Subir archivo a Supabase Storage
        upload_file_to_storage(ruta_storage, file)

        # 🔹 Registrar en tareas_entregadas
        tarea_entregada = TareaEntregada(entrega_id=entrega.id, nombre_original=file.filename,
                                        ruta_archivo=ruta_storage, tipo_mime=file.content_type, 
                                        tamanio_bytes=file.size)

        session.add(tarea_entregada)
        session.commit()

        return {"message": "Entrega realizada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/correcion-entregas/{entrega_id}")
def corregir_entrega(entrega_id: UUID, datos: CorreccionCreate, user=Depends(get_current_user),
                                                        session: Session = Depends(get_session)):
    try:
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
                raise HTTPException(401, "Usuario no encontrado")

        if usuario.perfil != PerfilUsuario.profesor:
            raise HTTPException(403, "Solo profesores pueden corregir")

        entrega = session.get(Entrega, entrega_id)

        if not entrega:
            raise HTTPException(404, "Entrega no encontrada")
    
        if entrega.estado == EstadosEntregas.corregido:
            raise HTTPException(400, "La entrega ya fue corregida")

        # 🔎 Validar que el profesor pertenece al curso de la tarea
        publicacion = session.get(Publicacion, entrega.publicacion_id)

        materia_curso_profesor = session.exec(select(CursoProfesor).where(CursoProfesor.profesor_id == usuario.id)
                                    .where(CursoProfesor.materia_curso_id == publicacion.materia_curso_id)).first()

        if not materia_curso_profesor:
            raise HTTPException(403, "No pertenece a este curso")

        # 🔥 Aplicar corrección
        entrega.nota = datos.nota
        entrega.comentario_profesor = datos.comentario_profesor
        entrega.fecha_actualizacion = datetime.now(timezone.utc)
        entrega.corregido_por_id = usuario.id
        entrega.estado = EstadosEntregas.corregido

        session.add(entrega)
        session.commit()
        session.refresh(entrega)

        return entrega
    
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{publicacion_id}", response_model=PublicacionUpdate)
def actualizar_publicacion(publicacion_id: UUID, data: PublicacionUpdate, user=Depends(get_current_user), 
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

@router.get("/archivos/{archivo_id}/download")
def descargar_archivo(archivo_id: UUID, user=Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        usuario = session.get(Usuario, user["sub"])
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        ruta = None
        publicacion = None # 

        # 1️⃣ Intentar como archivo de publicación
        archivo_publicacion = session.get(ArchivosPublicacion, archivo_id)
        if archivo_publicacion:
            publicacion = session.get(Publicacion, archivo_publicacion.publicacion_id)
            ruta = archivo_publicacion.ruta_archivo

        else:
            # 2️⃣ Intentar como archivo de entrega
            archivo_entrega = session.get(TareaEntregada, archivo_id)
            if not archivo_entrega:
                raise HTTPException(404, "Archivo no encontrado")

            entrega = session.get(Entrega, archivo_entrega.entrega_id)
            if not entrega:
                raise HTTPException(404, "Entrega no encontrada")
        
            if usuario.perfil == PerfilUsuario.alumno and archivo_entrega:
                if entrega.alumno_id != usuario.id:
                    raise HTTPException(403, "No puede acceder a esta entrega")

            publicacion = session.get(Publicacion, entrega.publicacion_id)
            ruta = archivo_entrega.ruta_archivo

        if not publicacion:
            raise HTTPException(404, "Publicación no encontrada")

        # 🔐 Validación de acceso
        if usuario.perfil == PerfilUsuario.profesor:
            relacion = session.exec(select(CursoProfesor).where(CursoProfesor.materia_curso_id == publicacion.materia_curso_id,
                                                                CursoProfesor.profesor_id == usuario.id)).first()
            if not relacion:
                raise HTTPException(403, "No tiene acceso a esta materia")

        elif usuario.perfil == PerfilUsuario.alumno:
            relacion = session.exec(select(CursoAlumno).join(MateriaCurso, CursoAlumno.curso_id == MateriaCurso.curso_id).where(
                                    MateriaCurso.id == publicacion.materia_curso_id,CursoAlumno.alumno_id == usuario.id)).first()
            if not relacion:
                raise HTTPException(403, "No tiene acceso a esta materia")

        else:
            raise HTTPException(403, "Perfil no autorizado")

        signed_url = generate_signed_url(ruta, 600)
        return {"url": signed_url}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))