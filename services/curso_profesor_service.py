# services/curso_profesor_service.py

from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID

from models.curso_profesor import CursoProfesor
from schemas.profesor import ProfesorEnCursoMateriaCreate
from repositories.curso_profesor_repository import CursoProfesorRepository

class CursoProfesorService:

    def __init__(self, session: Session):
        self.session = session
        self.profesor_en_curso_repository = CursoProfesorRepository(session)

    def get_all(self, materia_curso_id: UUID | None = None) -> list[CursoProfesor]:
        """
        Obtener profesores asignados a cursos y materia.

        Este endpoint devuelve las relaciones entre **profesores y cursos y materia**
        registradas en el sistema. Permite filtrar opcionalmente por
        **curso_materia**.

        Parámetros:
        - **materia_curso_id (UUID, opcional)**  
        Identificador del curso. Si se proporciona, se devolverán únicamente
        los profesores asignados a ese curso.


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
            return self.profesor_en_curso_repository.get_all_with_filters(materia_curso_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener profesor_en_curso: {str(e)}"
            )

    def assign(self, data: ProfesorEnCursoMateriaCreate) -> CursoProfesor:
        """
        Asignar una materia y  curso a un profesor.

        Este Metodo permite registrar la asignación de un **profesor**
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
        - Si el profesor ya está asignado a ese curso en esa materia,
        se devuelve un error para evitar duplicados.

        Permisos:
        - Requiere autenticación.
        - Solo usuarios con rol **admin** pueden realizar esta operación.

        Proceso:
        1. Se verifica si el profesor ya está asignado al curso y materia.
        2. Si no existe la asignación, se crea un nuevo_profesor_en_curso registro `CursoProfesor`.
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
            existing = self.profesor_en_curso_repository.get_by_unique_fields(
                profesor_id=data.profesor_id,
                materia_curso_id=data.materia_curso_id
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="El profesor ya está asignado a ese curso en esa materia"
                )
            nuevo_profesor_en_curso = CursoProfesor(**data.model_dump())
            self.profesor_en_curso_repository.create(nuevo_profesor_en_curso)
            self.session.commit()
            self.session.refresh(nuevo_profesor_en_curso)
            return nuevo_profesor_en_curso

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
                detail=f"Error al crear profesor_curso: {str(e)}"
            )

    def delete(self, curso_profesor_id: UUID) -> None:
        """
        Eliminar la asignación de un profesor a un cursoy materia.

        Este Metodo elimina la relación existente entre un **profesor** y un **cursoy materia**
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
            curso_profesor = self.profesor_en_curso_repository.get_by_id(curso_profesor_id)
            if not curso_profesor:
                raise HTTPException(
                    status_code=404,
                    detail="CursoProfesor no encontrada"
                )
            self.profesor_en_curso_repository.delete(curso_profesor)
            self.session.commit()
            return {"message": "CursoProfesor eliminado correctamente"}
        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar profesor_curso: {str(e)}"
            )