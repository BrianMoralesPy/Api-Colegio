import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime, timezone
from uuid import uuid4
from services.configuration import upload_file_to_storage

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
def leer_datos_publicacion(publicacion_id: UUID, user=Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Endpoint para obtener la información de una publicación específica.

    El acceso se controla según el perfil del usuario:

    - ADMIN:
        Puede ver cualquier publicación, incluso si está inactiva.

    - PROFESOR:
        Puede ver todas las publicaciones que haya creado.
        También puede ver publicaciones activas de otras materias.
        No puede ver publicaciones inactivas creadas por otros profesores.

    - ALUMNO:
        Puede ver publicaciones activas de las materias en las que esté inscripto.
        No puede ver publicaciones inactivas.

    Args:
        publicacion_id (UUID):
            ID de la publicación que se desea consultar.

        user:
            Usuario autenticado obtenido desde el token JWT mediante la dependencia get_current_user.

        session (Session):
            Sesión de base de datos proporcionada por la dependencia get_session.

    Returns:
        PublicacionOut:
            Objeto con la información completa de la publicación.

    Raises:
        HTTPException:
            404 si el usuario o la publicación no existen.
            403 si el usuario no tiene permisos para acceder a la publicación.
            500 si ocurre un error interno.
    """
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
    """
    Endpoint para obtener los archivos adjuntos de una publicación.

    Permite recuperar todos los archivos asociados a una publicación
    de tipo tarea o material.

    Control de acceso:

    - ADMIN:
        Puede ver los archivos de cualquier publicación.

    - PROFESOR:
        Puede ver archivos de publicaciones pertenecientes a materias
        en las que esté asignado como profesor.

    - ALUMNO:
        Puede ver archivos de publicaciones activas de materias
        en las que esté inscripto.

    Args:
        publicacion_id (UUID):
            ID de la publicación de la cual se desean obtener los archivos.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        list[ArchivoPublicacionOut]:
            Lista de archivos asociados a la publicación.

    Raises:
        HTTPException:
            404 si el usuario o la publicación no existen.
            403 si el usuario no tiene acceso a la materia.
            500 si ocurre un error interno.
    """
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
    """
    Endpoint para crear una nueva publicación dentro de una materia de un curso.

    Tipos de publicación posibles:
    - aviso
    - tarea
    - material

    Control de acceso:

    - ADMIN:
        No puede crear publicaciones.

    - PROFESOR:
        Puede crear publicaciones únicamente en materias donde esté asignado.

    - ALUMNO:
        No puede crear publicaciones.

    Args:
        materia_curso_id (UUID):
            ID de la relación materia-curso donde se creará la publicación.

        data (PublicacionCreate):
            Datos necesarios para crear la publicación
            (título, descripción, tipo, fecha de entrega, etc.).

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        PublicacionOut:
            Objeto con la información de la publicación creada.

    Raises:
        HTTPException:
            404 si la materia del curso no existe.
            403 si el usuario no tiene permiso para publicar.
            500 si ocurre un error interno durante la creación.
    """
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
    """
    Endpoint para subir archivos adjuntos a una publicación.

    Solo permite subir archivos a publicaciones de tipo:
    - tarea
    - material

    Los archivos se almacenan en Supabase Storage y se registra
    su metadata en la base de datos.

    Control de acceso:

    - ADMIN:
        No puede subir archivos.

    - PROFESOR:
        Puede subir archivos únicamente en publicaciones que haya creado
        o en materias donde esté asignado.

    - ALUMNO:
        No puede subir archivos.

    Args:
        publicacion_id (UUID):
            ID de la publicación a la cual se adjuntará el archivo.

        file (UploadFile):
            Archivo enviado mediante formulario multipart/form-data.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        ArchivoPublicacionOut:
            Información del archivo subido.

    Raises:
        HTTPException:
            404 si la publicación no existe.
            400 si la publicación es de tipo aviso.
            403 si el usuario no tiene permiso.
            500 si ocurre un error al subir el archivo.
    """
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
    """
    Endpoint para que un alumno entregue una tarea.

    Permite subir un archivo asociado a una publicación de tipo tarea.
    El archivo se almacena en Supabase Storage y se registra en la base de datos.

    Control de acceso:

    - ADMIN:
        No puede entregar tareas.

    - PROFESOR:
        No puede entregar tareas.

    - ALUMNO:
        Puede entregar tareas únicamente si:
        - La publicación es de tipo tarea.
        - La tarea no está vencida.
        - El alumno pertenece al curso de la materia.

    Args:
        publicacion_id (UUID):
            ID de la publicación de tipo tarea.

        file (UploadFile):
            Archivo enviado por el alumno como entrega.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        dict:
            Mensaje confirmando que la entrega fue realizada correctamente.

    Raises:
        HTTPException:
            404 si la publicación no existe.
            400 si la tarea está vencida o no es del tipo correcto.
            403 si el alumno no pertenece al curso.
            500 si ocurre un error interno.
    """
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
    """
    Endpoint para que un profesor corrija una entrega de tarea.

    Permite asignar:
    - nota
    - comentario del profesor

    Control de acceso:

    - ADMIN:
        No puede corregir entregas.

    - PROFESOR:
        Puede corregir entregas únicamente de materias
        en las que esté asignado.

    - ALUMNO:
        No puede corregir entregas.

    Args:
        entrega_id (UUID):
            ID de la entrega que se desea corregir.

        datos (CorreccionCreate):
            Información de la corrección (nota y comentario).

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        Entrega:
            Objeto actualizado con la corrección aplicada.

    Raises:
        HTTPException:
            404 si la entrega no existe.
            400 si la entrega ya fue corregida.
            403 si el profesor no pertenece a la materia.
            500 si ocurre un error interno.
    """
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
    """
    Endpoint para actualizar una publicación existente.

    Solo se actualizarán los campos enviados en la request,
    permitiendo un comportamiento similar a PATCH.

    Control de acceso:

    - ADMIN:
        No puede actualizar publicaciones.

    - PROFESOR:
        Puede actualizar únicamente publicaciones que haya creado.

    - ALUMNO:
        No puede actualizar publicaciones.

    Args:
        publicacion_id (UUID):
            ID de la publicación que se desea modificar.

        data (PublicacionUpdate):
            Datos que se desean actualizar.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        PublicacionUpdate:
            Información actualizada de la publicación.

    Raises:
        HTTPException:
            404 si la publicación no existe.
            403 si el usuario no tiene permisos.
            500 si ocurre un error durante la actualización.
    """
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
    """
    Endpoint para eliminar una publicación.

    El comportamiento depende del perfil del usuario:

    - ADMIN:
        Puede eliminar cualquier publicación definitivamente (hard delete).

    - PROFESOR:
        Puede eliminar únicamente publicaciones que haya creado.
        La eliminación es lógica (soft delete), marcando la publicación como inactiva.

    - ALUMNO:
        No puede eliminar publicaciones.

    Args:
        publicacion_id (UUID):
            ID de la publicación a eliminar.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        dict:
            Mensaje confirmando la eliminación.

    Raises:
        HTTPException:
            404 si la publicación no existe.
            403 si el usuario no tiene permisos.
            500 si ocurre un error interno.
    """
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
    """
    Endpoint para generar una URL firmada de descarga de un archivo.

    Puede tratarse de:
    - archivo de publicación
    - archivo de entrega de tarea

    Se valida que el usuario tenga acceso a la materia
    antes de permitir la descarga.

    Control de acceso:

    - ADMIN:
        Puede descargar cualquier archivo.

    - PROFESOR:
        Puede descargar archivos de materias donde esté asignado.

    - ALUMNO:
        Puede descargar archivos de materias donde esté inscripto.
        Solo puede acceder a sus propias entregas.

    Args:
        archivo_id (UUID):
            ID del archivo almacenado.

        user:
            Usuario autenticado obtenido desde el token JWT.

        session (Session):
            Sesión de base de datos.

    Returns:
        dict:
            URL firmada temporal para descargar el archivo desde Supabase Storage.

    Raises:
        HTTPException:
            404 si el archivo no existe.
            403 si el usuario no tiene permisos.
            500 si ocurre un error interno.
    """
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
        elif usuario.perfil == PerfilUsuario.admin:
            pass

        else:
            raise HTTPException(403, "Perfil no autorizado")

        signed_url = generate_signed_url(ruta, 600)
        return {"url": signed_url}

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))