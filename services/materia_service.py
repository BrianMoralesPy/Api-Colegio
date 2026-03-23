from fastapi import HTTPException
from sqlmodel import Session
from uuid import UUID

from schemas.materia import MateriaCreate,MateriaOut,MateriaUpdate
from models.materia import Materia
from repositories.materia_repository import MateriaRepository

class MateriaService:
    def __init__(self, session: Session):
        self.session = session
        self.materia_repo = MateriaRepository(session)

    def get_materias(self) -> list[MateriaOut]:
        """
        Metodo para obtener todos las materias registrados en el sistema.

        Requiere que el usuario autenticado tenga rol de administrador.

        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role, que asegura que tenga rol de administrador.

        Retorna una lista de objetos **MateriaOut** con la información de cada materia registrada,
        incluyendo nombre, codigo, activo , descripcion , fechas de creación y modificación.
        """
        try:
            materias = self.materia_repo.get_all()
            return [MateriaOut.model_validate(m) for m in materias]
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    def get_materia(self, materia_id:UUID) -> MateriaOut:
        """
        Metodo para obtener una materia específica a partir de su ID.

        Requiere autenticación y rol de administrador.

        - **materia_id**: Identificador único del materia que se desea consultar.
        - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **MateriaOut** con los datos de la materia solicitado.

        Si la materia no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
        """
        try:
            materia = self.materia_repo.get_by_id(materia_id)

            if not materia:
                raise HTTPException(status_code=404, detail="Materia no encontrada")

            return MateriaOut.model_validate(materia)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    def create_materia(self, materia_data:MateriaCreate):
        """
        Metodo para crear una materia nueva.

        Requiere autenticación y rol de administrador.

        - **session**: Sesión de base de datos proporcionada por la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **MateriaCreate** con los datos de la  materia creada.

        Si el materia no se pudo crear, lanza una excepción HTTP 404.
        Si ocurre un error inesperado en el servidor, lanza una excepción HTTP 500.
        """
        try: 
            nueva_materia = Materia.model_validate(materia_data)
            
            self.materia_repo.create(nueva_materia) # puede funcionar para crear o updatear
            self.session.commit()
            self.session.refresh(nueva_materia)
            
            return MateriaOut.model_validate(nueva_materia)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al crear materia")


    def update_materia(self, materia_id:UUID, materia_data:MateriaUpdate):
        """
        Metodo para actualizar una materia existente.

        Requiere autenticación y rol de administrador.

        - **materia_id**: ID de la materia que se desea actualizar.
        - **materia_data**: Objeto del esquema MateriaUpdate que contiene los nuevos valores
        para los campos de la materia (nombre, descripcion, codigo y activo).
        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Retorna un objeto **MateriaOut** con los datos actualizados del materia.

        Si la materia no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado durante la actualización, lanza una excepción HTTP 500.
        """
        try:
            materia = self.materia_repo.get_by_id(materia_id)
            if not materia:
                raise HTTPException(status_code=404, detail="Materia no encontrada")

            update_data = materia_data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(materia, key, value)
            
            self.materia_repo.create(materia) # puede funcionar para crear o updatear
            self.session.commit()
            self.session.refresh(materia)
            return MateriaOut.model_validate(materia)
            
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al modificar materia")


    def delete_materia(self, materia_id: UUID):
        """
        Metodo para eliminar una materia del sistema.

        Requiere autenticación y rol de administrador.

        - **materia_id**: Identificador único de la materia que se desea eliminar.
        - **session**: Sesión de base de datos obtenida mediante la dependencia get_session.
        - **user**: Usuario autenticado validado mediante require_role.

        Si la materia existe, se elimina de la base de datos y se devuelve un mensaje de confirmación.

        Si la materia no existe, lanza una excepción HTTP 404.
        Si ocurre un error inesperado durante la eliminación, lanza una excepción HTTP 500.
        """
        try:
            materia = self.materia_repo.get_by_id(materia_id)
            if not materia:
                raise HTTPException(status_code=404, detail="Materia no encontrada")

            self.materia_repo.delete(materia)
            self.session.commit()

            return {"detail": "Materia eliminada exitosamente"}
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Error al eliminar materia")