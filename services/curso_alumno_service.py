# services/curso_alumno_service.py

from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID

from models.curso_alumno import CursoAlumno
from schemas.alumno import AlumnoEnCursoCreate
from repositories.curso_alumno_repository import CursoAlumnoRepository


class CursoAlumnoService:

    def __init__(self, session: Session):
        self.session = session
        self.curso_alumno_repository = CursoAlumnoRepository(session)
    def get_all(self,curso_id: UUID | None = None,
                ciclo_lectivo: int | None = None) -> list[CursoAlumno]:
        """
        Obtener alumnos asignados a cursos.

        Este Metodo devuelve las relaciones entre **alumnos y cursos**
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
        - Solo usuarios con rol **admin** pueden acceder a este Metodo.

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
            return self.curso_alumno_repository.get_all_with_filters(
                    curso_id=curso_id,
                    ciclo_lectivo=ciclo_lectivo)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener alumnos_curso: {str(e)}"
            )
    def assign(self, data: AlumnoEnCursoCreate) -> CursoAlumno:
        """
        Asignar un curso a un alumno.

        Este Metodo permite registrar la asignación de un **alumno**
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
            existing = self.curso_alumno_repository.get_by_unique_fields(
                            alumno_id=data.alumno_id,
                            curso_id=data.curso_id,
                            ciclo_lectivo=data.ciclo_lectivo)

            if existing:
                raise HTTPException(
                        status_code=400,
                        detail="El alumno ya está asignado a ese curso en ese ciclo lectivo")

            nuevo_alumno_en_curso = CursoAlumno(**data.model_dump())

            self.curso_alumno_repository.create(nuevo_alumno_en_curso)
            self.session.commit()
            self.session.refresh(nuevo_alumno_en_curso)

            return nuevo_alumno_en_curso

        except IntegrityError:
            self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="No se pudo guardar el registro debido a una restricción de la base de datos"
            )

        except HTTPException:
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear alumno_curso: {str(e)}"
            )
        
    def delete(self, curso_alumno_id: UUID) -> None:
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
            curso_alumno = self.curso_alumno_repository.get_by_id(curso_alumno_id)

            if not curso_alumno:
                raise HTTPException(
                    status_code=404,
                    detail="CursoAlumno no encontrada"
                )

            self.curso_alumno_repository.delete(curso_alumno)
            self.session.commit()

            return {"message": "CursoAlumno eliminado correctamente"}

        except HTTPException:
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar alumno_curso: {str(e)}"
            )