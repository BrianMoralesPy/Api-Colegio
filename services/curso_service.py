from fastapi import HTTPException
from sqlmodel import Session
from uuid import UUID

from schemas.curso import CursoCreate,CursoOut,CursoUpdate
from models.curso import Curso
from repositories.curso_repository import CursoRepository

class CursoService:
    def __init__(self, session:Session):
        self.session = session
        self.curso_repo = CursoRepository(session)

    def get_cursos(self) -> list[CursoOut]:
        """
        Metodo para obtener todos los cursos registrados en el sistema.

        Requiere que el usuario autenticado tenga rol de administrador.

        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role, que asegura que tenga rol de administrador.

        Retorna una lista de objetos **CursoOut** con la información de cada curso registrada,
        incluyendo nombre, turno, activo , nivel , fechas de creación y modificación.
        """
        try:
            cursos = self.curso_repo.get_all()
            return [CursoOut.model_validate(c) for c in cursos]
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    def get_curso(self, curso_id: UUID) -> CursoOut:
        """
        Metodo para obtener un curso específico a partir de su ID.

        Requiere autenticación y rol de administrador.

        - **curso_id**: Identificador único del curso que se desea consultar.
        - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **CursoOut** con los datos de el curso solicitado.

        Si el curso no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
        """
        try:
            curso = self.curso_repo.get_by_id(curso_id)

            if not curso:
                raise HTTPException(status_code=404, detail="Curso no encontrada")

            return CursoOut.model_validate(curso)
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    def create_curso(self, curso_data: CursoCreate):
        """
        Metodo para crear un curso nuevo.

        Requiere autenticación y rol de administrador.

        - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **CursoCreate** con los datos del  curso creado.

        Si el curso no se pudo crear, lanza una excepción HTTP 404.
        Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
        """
        try:
            nuevo_curso = Curso.model_validate(curso_data)

            self.curso_repo.create(nuevo_curso) # puede funcionar para crear o updatear
            self.session.commit()
            self.session.refresh(nuevo_curso)
            
            return CursoOut.model_validate(nuevo_curso)
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al crear curso")


    def update_curso(self, curso_id: UUID, curso_data: CursoUpdate):
        """
        Metodo para actualizar un curso existente.

        Requiere autenticación y rol de administrador.

        - **curso_id**: ID del curso que se desea actualizar.
        - **curso_data**: Objeto del esquema CursoUpdate que contiene los nuevos valores
        para los campos de la curso (nombre, activo, turno y nivel).
        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **CursoOut** con los datos actualizados del curso.

        Si la curso no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado durante la actualización, lanza una excepción HTTP 500.
        """
        try:
            curso = self.curso_repo.get_by_id(curso_id)
            if not curso:
                raise HTTPException(status_code=404, detail="Curso no encontrada")

            update_data = curso_data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(curso, key, value)
            
            self.curso_repo.create(curso) # puede funcionar para crear o updatear
            self.session.commit()
            self.session.refresh(curso)
            
            return CursoOut.model_validate(curso)
        
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al modificar curso")


    def delete_curso(self, curso_id: UUID):
        """
        Metodo para eliminar un curso del sistema.

        Requiere autenticación y rol de administrador.

        - **curso_id**: Identificador único del curso que se desea eliminar.
        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Si el curso existe, se elimina de la base de datos y se devuelve un mensaje de confirmación.

        Si el curso no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado durante la eliminación, lanza una excepción HTTP 500.
        """
        try:
            curso = self.curso_repo.get_by_id(curso_id)
            if not curso:
                raise HTTPException(status_code=404, detail="Curso no encontrada")

            self.curso_repo.delete(curso)
            self.session.commit()

            return {"detail": "Curso eliminada exitosamente"}
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al eliminar curso")