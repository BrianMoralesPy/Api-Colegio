from fastapi import APIRouter, Depends, HTTPException # Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session, select # Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from services.configuration import supabase_admin, get_session, require_role
from models.alumno import Alumno
from uuid import UUID 
from models.usuario import Usuario
from models.historial_contrasenas import HistorialContrasenas
from models.curso_alumno import CursoAlumno
from schemas.usuario import UsuarioUpdate
from schemas.alumno import AlumnoUpdate,AlumnoOutFull,AlumnoEnCursoBasic, AlumnoEnCursoCreate, AlumnoCursoOutFull
from models.enums import PerfilUsuario

router = APIRouter(prefix="/alumnos", tags=["Alumnos"]) # Crea un router de FastAPI con el prefijo "/alumnos" para agrupar 
                                                        # las rutas relacionadas con los alumnos y asigna la etiqueta "Alumnos" 
                                                        # para la documentación automática

@router.get("/", response_model=list[AlumnoOutFull])
def get_alumnos(session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> list[AlumnoOutFull]:
    """
    Obtener la lista de todos los alumnos.

    Este endpoint devuelve todos los alumnos registrados en el sistema junto con
    la información del usuario asociado (nombre, apellido, edad, etc.).

    Permisos:
    - Requiere autenticación.
    - Solo los usuarios con rol **admin** pueden acceder a esta información.

    Retorna:
    - **list[AlumnoOutFull]**: Lista de alumnos con su información personal y académica.

    Errores:
    - **500 Internal Server Error**: Si ocurre un error inesperado al consultar la base de datos.
    """
    try:

        alumnos = session.query(Alumno).all()   # Obtiene todos los registros de alumnos de la base de datos utilizando la sesiónproporcionada 
                                                # por la función get_session a través de Depends.
        respuesta = []

        for alumno in alumnos:
            usuario = session.get(Usuario, alumno.id)
            if not usuario:
                continue
            respuesta.append(AlumnoOutFull(id=alumno.id, nombre=usuario.nombre, apellido=usuario.apellido, edad=usuario.edad, perfil=usuario.perfil,
                                            ruta_foto=usuario.ruta_foto, legajo=alumno.legajo, fecha_ingreso=alumno.fecha_ingreso, estado=alumno.estado,
                                            observaciones=alumno.observaciones, activo=alumno.activo))
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alumno: {str(e)}")

# ---- Seccion de Alumno en Curso -----
@router.get("/curso-alumno", response_model=list[AlumnoCursoOutFull])
def get_alumno_en_curso(curso_id: UUID | None = None, ciclo_lectivo: int | None = None,session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))) -> list[AlumnoCursoOutFull]:
    """
    Obtener alumnos asignados a cursos.

    Este endpoint devuelve las relaciones entre **alumnos y cursos**
    registradas en el sistema. Permite filtrar opcionalmente por
    **curso** y/o **ciclo lectivo**.

    Parámetros:
    - **curso_id (UUID, opcional)**  
      Identificador del curso. Si se proporciona, se devolverán únicamente
      los alumnos asignados a ese curso.

    - **ciclo_lectivo (int, opcional)**  
      Año del ciclo lectivo. Si se especifica, se devolverán solo los alumnos
      asignados en ese ciclo lectivo.

    Comportamiento:
    - Si no se envían filtros, se devuelven **todas las asignaciones
      de alumnos a cursos** registradas en el sistema.
    - Los filtros pueden combinarse para obtener resultados más específicos.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden acceder a este endpoint.

    Optimización:
    - Se utilizan **selectinload()** para precargar las relaciones `curso`
      y `alumno`, evitando el problema **N+1 queries** y mejorando
      el rendimiento de la consulta.

    Retorna:
    - **list[AlumnoCursoOutFull]**: Lista de relaciones alumno-curso
      con la información completa del alumno y del curso.

    Notas:
    - Si no se encuentran registros que coincidan con los filtros,
      se devuelve una **lista vacía**.

    Errores:
    - **500 Internal Server Error**: Si ocurre un error inesperado
      durante la consulta a la base de datos.
    """
    try:
        # Construir la consulta base con las relaciones necesarias para evitar N+1
        statement = (select(CursoAlumno).options(selectinload(CursoAlumno.curso),selectinload(CursoAlumno.alumno)
                                                .selectinload(Alumno.usuario)))
        if curso_id:
            # Filtrar por curso_id si se proporciona
            statement = statement.where(CursoAlumno.curso_id == curso_id)
        
        if ciclo_lectivo:
            # Filtrar por ciclo_lectivo si se proporciona
            statement = statement.where(CursoAlumno.ciclo_lectivo == ciclo_lectivo)
        # Ejecutar la consulta y obtener los resultados
        
        alumnos_curso = session.exec(statement).all()
        return alumnos_curso   # SQLModel se encargará de convertir cada objeto CursoAlumno en AlumnoCursoOutFull 
                                # gracias a la configuración de from_attributes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alumnos_curso: {str(e)}")

@router.post("/asignar-curso", response_model=AlumnoEnCursoBasic)
def asignar_curso_a_alumno(data: AlumnoEnCursoCreate, session: Session = Depends(get_session),
                                user=Depends(require_role(PerfilUsuario.admin))) -> AlumnoEnCursoBasic:
    """
    Asignar un curso a un alumno.

    Este endpoint permite registrar la asignación de un **alumno**
    a un **curso** para un **ciclo lectivo específico**.

    Parámetros:
    - **data (AlumnoEnCursoCreate)**  
      Objeto con la información necesaria para realizar la asignación.

      Campos esperados:
      - **alumno_id (UUID)**: Identificador del alumno.
      - **curso_id (UUID)**: Identificador del curso al que se asignará el alumno.
      - **ciclo_lectivo (int)**: Año del ciclo lectivo en el que se realiza la asignación.
      - **estado (Enum / str)**: Estado de la asignación del alumno en el curso
        (por ejemplo: activo, aprobado, recursando, etc.).

    Validaciones:
    - Antes de crear la asignación, se verifica si ya existe un registro
      con la misma combinación de **alumno, curso y ciclo lectivo**.
    - Si el alumno ya está asignado a ese curso en ese ciclo lectivo,
      se devuelve un error para evitar duplicados.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se verifica si el alumno ya está asignado al curso en el mismo ciclo lectivo.
    2. Si no existe la asignación, se crea un nuevo registro `CursoAlumno`.
    3. Se guarda el registro en la base de datos (`commit`).
    4. Se refresca el objeto para obtener los valores generados automáticamente.

    Retorna:
    - **AlumnoEnCursoBasic**: Información de la asignación creada.

    Errores:
    - **400 Bad Request**
        - Si el alumno ya está asignado a ese curso en ese ciclo lectivo.
        - Si ocurre una violación de restricción única en la base de datos.
    - **500 Internal Server Error**
        - Si ocurre un error inesperado durante la creación del registro.
    """

    try:
        # Validar que el alumno no esté ya en ese curso ese año
        statement = select(CursoAlumno).where(CursoAlumno.alumno_id == data.alumno_id,
                                                CursoAlumno.curso_id == data.curso_id,
                                                CursoAlumno.ciclo_lectivo == data.ciclo_lectivo)

        existing = session.exec(statement).first()

        if existing:
            raise HTTPException(status_code=400, detail="El alumno ya está asignado a ese curso en ese ciclo lectivo")

        nuevo_alumno_en_curso = CursoAlumno(**data.model_dump())

        session.add(nuevo_alumno_en_curso)
        session.commit()
        session.refresh(nuevo_alumno_en_curso)

        return nuevo_alumno_en_curso

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="No se pudo guardar el registro debido a una restricción de la base de datos")

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error al crear alumno_curso: {str(e)}")

@router.delete("/eliminar-de-curso/{curso_alumno_id}")
def delete_alumno_de_curso(curso_alumno_id: UUID, session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))  ) -> dict:
    """
    Eliminar la asignación de un alumno a un curso.

    Este endpoint elimina la relación existente entre un **alumno** y un **curso**
    registrada en la tabla `CursoAlumno`.

    Parámetros:
    - **curso_alumno_id (UUID)**  
      Identificador único de la relación alumno-curso que se desea eliminar.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se busca la relación `CursoAlumno` utilizando su ID.
    2. Si no existe, se devuelve un error **404 Not Found**.
    3. Si existe, se elimina el registro de la base de datos.
    4. Se realiza `commit` para confirmar la eliminación.

    Retorna:
    - **dict**: Mensaje indicando que la eliminación fue exitosa.

    Errores:
    - **404 Not Found**: Si la asignación no existe.
    - **500 Internal Server Error**: Si ocurre un error inesperado durante la operación.
    """
    try:
        # Buscar la relación por su ID
        curso_alumno = session.get(CursoAlumno, curso_alumno_id) 

        if not curso_alumno:
            raise HTTPException(status_code=404, detail="CursoAlumno no encontrada")

        session.delete(curso_alumno)
        session.commit()

        return {"message": "CursoAlumno eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar alumno_curso: {str(e)}")
# ---- Seccion de Alumno en Curso FIN -----

@router.get("/{alumno_id}", response_model=AlumnoOutFull)
def get_alumno(alumno_id: UUID,session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> AlumnoOutFull:
    """
    Obtener información completa de un alumno.

    Devuelve los datos del **alumno** junto con la información del
    **usuario asociado** (nombre, apellido, edad, etc.).

    Parámetros:
    - **alumno_id (UUID)**  
      Identificador único del alumno.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden acceder a esta información.

    Proceso:
    1. Se busca el registro del alumno en la base de datos.
    2. Se obtiene el usuario asociado al alumno.
    3. Se combinan los datos de ambas entidades para construir
       la respuesta `AlumnoOutFull`.

    Retorna:
    - **AlumnoOutFull**: Información completa del alumno.

    Errores:
    - **404 Not Found**: Si el alumno no existe.
    - **500 Internal Server Error**: Si el usuario asociado no existe o ocurre un error inesperado.
    """
    try:
        alumno = session.get(Alumno, alumno_id)  # Obtiene un registro de alumno específico de la base de datos utilizando su ID y la sesión 
                                                # proporcionada por la función get_session a través de Depends.
        if not alumno:
            raise HTTPException(404, "Alumno no encontrado")

        usuario = session.get(Usuario, alumno.id)
        if not usuario:
            raise HTTPException(500, "Usuario inconsistente")

        return AlumnoOutFull(id=alumno.id, nombre=usuario.nombre, apellido=usuario.apellido, edad=usuario.edad, perfil=usuario.perfil,
                                ruta_foto=usuario.ruta_foto, legajo=alumno.legajo, fecha_ingreso=alumno.fecha_ingreso, estado=alumno.estado,
                                observaciones=alumno.observaciones, activo=alumno.activo)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alumno: {str(e)}")

@router.put("/{alumno_id}")
def update_alumno(alumno_id:UUID,alumno_data:AlumnoUpdate,usuario_data:UsuarioUpdate,session:Session=Depends(get_session),
                    user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Actualizar la información de un alumno.

    Permite modificar los datos del **alumno** y del **usuario asociado**
    en una sola operación.

    Parámetros:
    - **alumno_id (UUID)**  
      Identificador del alumno que se desea actualizar.

    - **alumno_data (AlumnoUpdate)**  
      Datos del alumno que se desean actualizar.  
      Solo se modificarán los campos enviados en el request.

    - **usuario_data (UsuarioUpdate)**  
      Datos del usuario asociado al alumno que se desean actualizar.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se busca el alumno en la base de datos.
    2. Se obtiene el usuario asociado.
    3. Se actualizan dinámicamente los campos enviados en el request.
    4. Se guardan los cambios en la base de datos.

    Retorna:
    - **dict**: Mensaje indicando que la actualización fue exitosa.

    Errores:
    - **404 Not Found**: Si el alumno no existe.
    - **500 Internal Server Error**: Si el usuario asociado es inconsistente o ocurre un error inesperado.
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        session.rollback() # Si ocurre un error durante la actualización, se realiza un rollback de la sesión para deshacer cualquier cambio realizado en la base de datos.
        raise HTTPException(status_code=500, detail=f"Error al actualizar alumno: {str(e)}")

@router.delete("/{alumno_id}")
def delete_alumno(alumno_id: UUID,session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Eliminar definitivamente un alumno del sistema.

    Este endpoint elimina:
    - El registro del **alumno**
    - El **usuario asociado**
    - El historial de contraseñas del usuario
    - El usuario en **Supabase Auth**

    Parámetros:
    - **alumno_id (UUID)**  
      Identificador del alumno que se desea eliminar.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se obtiene el alumno desde la base de datos.
    2. Se obtiene el usuario asociado.
    3. Se elimina el historial de contraseñas del usuario.
    4. Se eliminan los registros de `Alumno` y `Usuario`.
    5. Se confirma la transacción en la base de datos.
    6. Se elimina el usuario en **Supabase Auth**.

    Retorna:
    - **dict**: Mensaje indicando que el alumno fue eliminado.

    Errores:
    - **404 Not Found**: Si el alumno no existe.
    - **500 Internal Server Error**: Si ocurre un error durante la eliminación.
    """
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
        supabase_admin.auth.admin.delete_user(str(usuario.id))

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar alumno: {str(e)}")

    return {"detail": "Alumno eliminado definitivamente"}