# services/materia_curso_service.py

from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID

from models.materia_curso import MateriaCurso
from schemas.materia_curso import MateriaCursoCreate
from repositories.materia_curso_repository import MateriaCursoRepository


class MateriaCursoService:

    def __init__(self, session: Session):
        self.session = session
        self.materia_curso_respository = MateriaCursoRepository(session)

    def create(self, data: MateriaCursoCreate) -> MateriaCurso:
        """
        Crear una relación entre una materia y un curso.

        Este metodo permite asignar una **materia** a un **curso** para un
        determinado **ciclo lectivo**. Cada combinación de `curso`, `materia`
        y `ciclo_lectivo` debe ser única dentro del sistema.

        Parámetros:
        - **data (MateriaCursoCreate)**: Objeto con la información necesaria
        para crear la relación entre la materia y el curso.

        Campos esperados:
        - **curso_id (UUID)**: Identificador del curso al que se asignará la materia.
        - **materia_id (UUID)**: Identificador de la materia que se asignará.
        - **ciclo_lectivo (int)**: Año del ciclo lectivo en el que la materia
            estará asociada al curso.

        Validaciones:
        - Antes de crear el registro, se verifica si ya existe una relación con
        el mismo `curso_id`, `materia_id` y `ciclo_lectivo`.
        - Si la relación ya existe, se devuelve un error para evitar duplicados.

        Permisos:
        - Solo los usuarios con rol **admin** pueden crear relaciones
        entre materias y cursos.

        Proceso:
        1. Se valida que no exista una relación previa con los mismos datos.
        2. Se crea una nueva instancia del modelo `MateriaCurso`.
        3. Se agrega el registro a la sesión de base de datos.
        4. Se realiza el `commit` para guardar los cambios.
        5. Se refresca el objeto para obtener valores generados automáticamente
        (por ejemplo, el ID).

        Retorna:
        - **MateriaCursoOutStandar**: La relación creada entre la materia
        y el curso.

        Errores:
        - **400 Bad Request**:
            - Si la materia ya está asignada a ese curso en ese ciclo lectivo.
            - Si ocurre una violación de restricción única en la base de datos.
        - **500 Internal Server Error**:
            - Si ocurre un error inesperado durante la creación del registro.
        """
        try:
            existing = self.materia_curso_respository.get_by_unique_fields(
                                                    curso_id=data.curso_id,
                                                    materia_id=data.materia_id,
                                                    ciclo_lectivo=data.ciclo_lectivo)

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Esta materia ya está asignada a ese curso en ese ciclo lectivo"
                )

            nueva_relacion = MateriaCurso(**data.model_dump())

            self.materia_curso_respository.create(nueva_relacion)
            self.session.commit()
            self.session.refresh(nueva_relacion)

            return nueva_relacion

        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=400, detail="Registro duplicado o violación de restricción")

        except HTTPException:
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear materia_curso: {str(e)}")

    def get_all(self,curso_id: UUID | None = None, 
                ciclo_lectivo: int | None = None) -> list[MateriaCurso]:
        """
        Obtener las materias asignadas a cursos.
        Este Metodo devuelve la lista de relaciones **Materia-Curso** registradas
        en el sistema. Permite aplicar filtros opcionales por curso y/o ciclo lectivo.
        Parámetros:
        - **curso_id** (UUID, opcional):  
        Identificador del curso. Si se proporciona, solo se devolverán las materias
        asociadas a ese curso.

        - **ciclo_lectivo** (int, opcional):  
        Año del ciclo lectivo. Si se especifica, se devolverán únicamente las materias
        correspondientes a ese año académico.

        Comportamiento:
        - Si no se envía ningún filtro, se devolverán **todas las materias asociadas a cursos**.
        - Si se envía uno o ambos filtros, la consulta se ajustará dinámicamente.

        Optimización:
        - Se utilizan **selectinload()** para precargar las relaciones `curso` y `materia`,
        evitando el problema **N+1 queries** y mejorando el rendimiento de la consulta.

        Permisos:
        - Requiere que el usuario autenticado tenga el rol **admin**.

        Retorna:
        - **list[MateriaCursoOutFull]**: Lista de relaciones materia-curso con la
        información completa del curso y la materia.

        Errores:
        - **500 Internal Server Error**: Si ocurre un error inesperado durante la consulta.
        """

        try:
            return self.materia_curso_respository.get_all_with_filters(curso_id=curso_id,
                                                                    ciclo_lectivo=ciclo_lectivo)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener materias_curso: {str(e)}"
            )


    def delete(self, materia_curso_id: UUID) -> None:
        """
        Eliminar una relación entre una materia y un curso.

        Este Metodo permite eliminar una relación existente entre una
        **materia**, un **curso** y un **ciclo lectivo** registrada en el sistema.

        Parámetros:
        - **materia_curso_id (UUID)**:  
        Identificador único de la relación `MateriaCurso` que se desea eliminar.

        Permisos:
        - Solo los usuarios con rol **admin** pueden eliminar relaciones
        entre materias y cursos.

        Proceso:
        1. Se busca la relación `MateriaCurso` en la base de datos utilizando su ID.
        2. Si la relación no existe, se devuelve un error **404 Not Found**.
        3. Si existe, se elimina el registro de la base de datos.
        4. Se realiza `commit` para confirmar los cambios.

        Retorna:
        - **dict**: Un mensaje indicando que la relación fue eliminada correctamente.

        Ejemplo de respuesta:
        ```
        {
            "message": "MateriaCurso eliminada correctamente"
        }
        ```

        Errores:
        - **404 Not Found**: Si no existe una relación con el `materia_curso_id` proporcionado.
        - **500 Internal Server Error**: Si ocurre un error inesperado durante la eliminación.
        """
        
        try:
            materia_curso = self.materia_curso_respository.get_by_id(materia_curso_id)

            if not materia_curso:
                raise HTTPException(
                    status_code=404,
                    detail="MateriaCurso no encontrada"
                )

            self.materia_curso_respository.delete(materia_curso)
            self.session.commit()

        except HTTPException:
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar materia_curso: {str(e)}"
            )
"""
eyJhbGciOiJIUzI1NiIsImtpZCI6IjFneWtoTjk4cVV6SHV4disiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2Zja2R6Y2tkemxiZHFwYmllcWl3LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1NzM0NmZkYS0xODU1LTRiNjctYWQ0Zi1kNTY4YjQ2YTNlZTUiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc0Mjk4MjUwLCJpYXQiOjE3NzQyOTQ2NTAsImVtYWlsIjoiYnJpYW5fYWRtaW4xMjNAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NzQyOTQ2NTB9XSwic2Vzc2lvbl9pZCI6ImUzMjU1YWM2LWU5OGYtNGI4Zi1iOGYxLWMzZGVjOWU2Y2I1NCIsImlzX2Fub255bW91cyI6ZmFsc2V9.4SxovjpQgS9o2g0KhK2WmDpncNdD6YrG39ZzyzBO-BE
"""