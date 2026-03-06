from fastapi import APIRouter, Depends, HTTPException# Importa las clases y funciones necesarias de FastAPI para crear rutas, manejar dependencias y lanzar excepciones HTTP
from sqlmodel import Session #  Importa la clase Session de SQLModel para manejar las sesiones de base de datos
from services.configuration import get_session,supabase_admin,require_role  # Importa la función get_session para obtener una sesión de base de datos y 
                                                # la instancia de Supabase desde el archivo de configuración 
from models.profesor import Profesor
from models.usuario import Usuario
from schemas.profesor import ProfesorUpdate, ProfesorOutFull, ProfesorCursoMateriaOutFull,ProfesorEnCursoMateriaCreate,ProfesorEnCursoMateriaBasic
from schemas.usuario import UsuarioUpdate
from models.historial_contrasenas import HistorialContrasenas
from models.enums import PerfilUsuario
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from models.curso_profesor import CursoProfesor
from models.materia_curso import MateriaCurso
from uuid import UUID

router = APIRouter(prefix="/profesores", tags=["Profesores"])   # Crea un router de FastAPI con el prefijo "/profesores" 
                                                                # para agrupar las rutas relacionadas con los profesores y 
                                                                # asigna la etiqueta "Profesores" para la documentación automática

@router.get("/", response_model=list[ProfesorOutFull])
def get_profesores(session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> list[ProfesorOutFull]:
    """
    Endpoint para obtener la lista completa de profesores registrados en el sistema.

    Requiere autenticación y que el usuario tenga rol de administrador.

    - **session**: Sesión de base de datos obtenida mediante la dependencia `get_session`.
    - **user**: Usuario autenticado validado mediante `require_role`, que asegura que tenga rol de administrador.

    Retorna una lista de objetos **ProfesorOutFull**, que contienen:
    - Información del profesor.
    - Datos del usuario asociado (nombre, apellido, edad, perfil y foto de perfil).

    Si ocurre un error inesperado durante la consulta, se lanza una excepción HTTP 500.
    """
    try:

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener profesores: {str(e)}")

@router.get("/curso-materia", response_model=list[ProfesorCursoMateriaOutFull])
def get_profesor_en_curso_materia(materia_curso_id: UUID | None = None, session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin)) ) -> list[ProfesorCursoMateriaOutFull]:
    """
    Obtener profesores asignados a cursos y materia.

    Este endpoint devuelve las relaciones entre **profesores y cursos y materia**
    registradas en el sistema. Permite filtrar opcionalmente por
    **curso** y/o **ciclo lectivo**.

    Parámetros:
    - **materia_curso_id (UUID, opcional)**  
      Identificador del curso. Si se proporciona, se devolverán únicamente
      los profesores asignados a ese curso.

    - **ciclo_lectivo (int, opcional)**  
      Año del ciclo lectivo. Si se especifica, se devolverán solo los profesores
      asignados en ese ciclo lectivo.

    Comportamiento:
    - Si no se envían filtros, se devuelven **todas las asignaciones
      de profesores a cursos y materia** registradas en el sistema.
    - Los filtros pueden combinarse para obtener resultados más específicos.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden acceder a este endpoint.

    Optimización:
    - Se utilizan **selectinload()** para precargar las relaciones `materia_curso`
      y `profesor`, evitando el problema **N+1 queries** y mejorando
      el rendimiento de la consulta.

    Retorna:
    - **list[ProfesorCursoMateriaOutFull]**: Lista de relaciones profesor-materia_curso
      con la información completa del profesor y del materia_curso.

    Notas:
    - Si no se encuentran registros que coincidan con los filtros,
      se devuelve una **lista vacía**.

    Errores:
    - **500 Internal Server Error**: Si ocurre un error inesperado
      durante la consulta a la base de datos.
    """
    try:
        statement = (select(CursoProfesor).options(selectinload(CursoProfesor.materia_curso),
                                                    selectinload(CursoProfesor.profesor).selectinload(Profesor.usuario)))

        if materia_curso_id:
            statement = statement.where(CursoProfesor.materia_curso_id == materia_curso_id)

        result = session.exec(statement).all()

        return [row[0] for row in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener profesor_en_curso: {str(e)}")
    
@router.post("/asignar-curso-materia", response_model=ProfesorEnCursoMateriaBasic)
def asignar_curso_y_materia_a_profesor(data: ProfesorEnCursoMateriaCreate, session: Session = Depends(get_session),
                                user=Depends(require_role(PerfilUsuario.admin))) -> ProfesorEnCursoMateriaBasic:
    """
    Asignar una materia y  curso a un profesor.

    Este endpoint permite registrar la asignación de un **profesor**
    a un **curso**  para una **materia específico**.

    Parámetros:
    - **data (ProfesorEnCursoMateriaCreate)**  
      Objeto con la información necesaria para realizar la asignación.

      Campos esperados:
      - **profesor_id (UUID)**: Identificador del profesor.
      - **materia_curso_id (UUID)**: Identificador del curso-materia al que se asignará el profesor.
      - **rol_en_curso (RolEnCurso)**: Rol que desempeñará el profesor en el curso-materia.

    Validaciones:
    - Antes de crear la asignación, se verifica si ya existe un registro
      con la misma combinación de **profesor, curso y materia**.
    - Si el profesor ya está asignado a ese curso en esa ciclo materia,
      se devuelve un error para evitar duplicados.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se verifica si el profesor ya está asignado al curso en el mismo ciclo lectivo.
    2. Si no existe la asignación, se crea un nuevo registro `CursoProfesor`.
    3. Se guarda el registro en la base de datos (`commit`).
    4. Se refresca el objeto para obtener los valores generados automáticamente.

    Retorna:
    - **ProfesorEnCursoMateriaBasic**: Información de la asignación creada.

    Errores:
    - **400 Bad Request**
        - Si el profesor ya está asignado a ese curso en esa materia.
        - Si ocurre una violación de restricción única en la base de datos.
    - **500 Internal Server Error**
        - Si ocurre un error inesperado durante la creación del registro.
    """

    try:
        # Validar que el profesor no esté ya en ese curso ese año
        statement = select(CursoProfesor).where(CursoProfesor.profesor_id == data.profesor_id,
                                                CursoProfesor.materia_curso_id == data.materia_curso_id)

        existing = session.exec(statement).first()

        if existing:
            raise HTTPException(status_code=400, detail="El profesor ya está asignado a ese curso en esa materia")

        nuevo_profesor_en_curso = CursoProfesor(**data.model_dump())

        session.add(nuevo_profesor_en_curso)
        session.commit()
        session.refresh(nuevo_profesor_en_curso)

        return nuevo_profesor_en_curso

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="No se pudo guardar el registro debido a una restricción de la base de datos")

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error al crear profesor_curso: {str(e)}")
    
@router.delete("/eliminar-de-curso-y-materia/{curso_profesor_id}")
def delete_profesor_de_curso_materia(curso_profesor_id: UUID, session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Eliminar la asignación de un profesor a un cursoy materia.

    Este endpoint elimina la relación existente entre un **profesor** y un **cursoy materia**
    registrada en la tabla `CursoProfesor`.

    Parámetros:
    - **curso_profesor_id (UUID)**  
      Identificador único de la relación profesor-curso y materiaque se desea eliminar.

    Permisos:
    - Requiere autenticación.
    - Solo usuarios con rol **admin** pueden realizar esta operación.

    Proceso:
    1. Se busca la relación `CursoProfesor` utilizando su ID.
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
        curso_profesor = session.get(CursoProfesor, curso_profesor_id) 

        if not curso_profesor:
            raise HTTPException(status_code=404, detail="CursoProfesor no encontrada")

        session.delete(curso_profesor)
        session.commit()

        return {"message": "CursoProfesor eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar profesor_curso: {str(e)}")
    
@router.get("/{profesor_id}", response_model=ProfesorOutFull)
def get_profesor(profesor_id: UUID, session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> ProfesorOutFull:
    """
    Endpoint para obtener la información completa de un profesor específico.

    Requiere autenticación y rol de administrador.

    - **profesor_id**: Identificador único del profesor que se desea consultar.
    - **session**: Sesión de base de datos proporcionada por `get_session`.
    - **user**: Usuario autenticado validado mediante `require_role`.

    Retorna un objeto **ProfesorOutFull** con:
    - Datos del profesor.
    - Datos del usuario asociado.

    Si el profesor no existe se lanza una excepción **HTTP 404**.
    Si el usuario asociado al profesor no existe se lanza una excepción **HTTP 500** por inconsistencia de datos.
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener profesores: {str(e)}")

@router.put("/{profesor_id}")
def update_profesor(profesor_id:UUID, profesor_data:ProfesorUpdate, usuario_data:UsuarioUpdate, 
                    session:Session=Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Endpoint para actualizar la información de un profesor existente.

    Permite modificar tanto los datos propios del profesor como los datos
    del usuario asociado.

    Requiere autenticación y rol de administrador.

    - **profesor_id**: ID del profesor que se desea actualizar.
    - **profesor_data**: Objeto del esquema `ProfesorUpdate` con los campos del profesor a modificar.
    - **usuario_data**: Objeto del esquema `UsuarioUpdate` con los campos del usuario asociados a modificar.
    - **session**: Sesión de base de datos proporcionada por `get_session`.
    - **user**: Usuario autenticado validado mediante `require_role`.

    Solo se actualizan los campos que estén presentes en los esquemas enviados.

    Retorna un diccionario con un mensaje de confirmación si la actualización se realiza correctamente.

    Posibles errores:
    - **404** si el profesor no existe.
    - **500** si el usuario asociado no existe o si ocurre un error inesperado.
    """
    try:

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener profesores: {str(e)}")

@router.delete("/{profesor_id}")
def delete_profesor(profesor_id: UUID,session: Session = Depends(get_session), user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Endpoint para eliminar definitivamente un profesor del sistema.

    Este proceso elimina:
    - El registro del profesor.
    - El usuario asociado.
    - El historial de contraseñas del usuario.
    - El usuario correspondiente en Supabase Auth.

    Requiere autenticación y rol de administrador.

    - **profesor_id**: Identificador único del profesor que se desea eliminar.
    - **session**: Sesión de base de datos proporcionada por `get_session`.
    - **user**: Usuario autenticado validado mediante `require_role`.

    Retorna un mensaje confirmando la eliminación del profesor.

    Posibles errores:
    - **404** si el profesor no existe.
    - **500** si el usuario asociado no existe o si ocurre un error durante el proceso de eliminación.
    """
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
