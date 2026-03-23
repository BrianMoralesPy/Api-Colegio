from fastapi import HTTPException
from sqlmodel import Session
from uuid import UUID

from schemas.profesor import ProfesorOutFull,ProfesorUpdate
from schemas.usuario import UsuarioUpdate
from infrastructure.supabase import supabase_admin

from repositories.profesor_repository import ProfesorRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.historial_repository import HistorialContrasenasRepository

class ProfesorService:
    def __init__(self, session:Session):
        self.session = session
        self.profesor_repo = ProfesorRepository(session)
        self.usuario_repo = UsuarioRepository(session)
        self.historial_repo = HistorialContrasenasRepository(session)
        
    def get_profesores(self) -> list[ProfesorOutFull]:
        """
        Metodo para obtener la lista completa de profesores registrados en el sistema.

        Requiere autenticación y que el usuario tenga rol de administrador.

        - **session**: Sesión de base de datos obtenida mediante la dependencia `get_session`.
        - **user**: Usuario autenticado validado mediante `require_role`, que asegura que tenga rol de administrador.

        Retorna una lista de objetos **ProfesorOutFull**, que contienen:
        - Información del profesor.
        - Datos del usuario asociado (nombre, apellido, edad, perfil y foto de perfil).

        Si ocurre un error inesperado durante la consulta, se lanza una excepción HTTP 500.
        """
        try:
            profesores = self.profesor_repo.get_all()
            return [ProfesorOutFull.model_validate(p) for p in profesores]

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Error al obtener profesores")

    def get_profesor(self, profesor_id:UUID) -> ProfesorOutFull:
        """
        Metodo para obtener la información completa de un profesor específico.

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
            profesor = self.profesor_repo.get_by_id(profesor_id)
            if not profesor:
                raise HTTPException(404, "Profesor no encontrado")

            usuario = self.usuario_repo.get_by_id(profesor.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")

            return ProfesorOutFull.model_validate(profesor)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, 
                                detail=f"Error al obtener profesor: {str(e)}")
        
    def update_profesor(self, profesor_id:UUID, profesor_data:ProfesorUpdate, 
                        usuario_data:UsuarioUpdate) -> dict:
        """
        Metodo para actualizar la información de un profesor existente.

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
            
            profesor = self.profesor_repo.get_by_id(profesor_id)
            if not profesor:
                raise HTTPException(404, "Profesor no encontrado")

            usuario = self.usuario_repo.get_by_id(profesor.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")
            
            # Actualizar Profesor
            for key, value in profesor_data.model_dump(exclude_unset=True).items():
                setattr(profesor, key, value)

            # Actualizar Usuario
            for key, value in usuario_data.model_dump(exclude_unset=True).items():
                setattr(usuario, key, value)

            self.session.commit()
            return {"detail": "Profesor actualizado correctamente"}
        
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar profesor: {str(e)}")

    def delete_profesor(self, profesor_id:UUID) -> dict:
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
        try:
            profesor = self.profesor_repo.get_by_id(profesor_id)
            if not profesor:
                raise HTTPException(404, "Profesor no encontrado")

            usuario = self.usuario_repo.get_by_id(profesor.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")

            self.historial_repo.delete_by_user_id(profesor.id)
            self.profesor_repo.delete(profesor)
            self.usuario_repo.delete(usuario) 

            self.session.commit()
            supabase_admin.auth.admin.delete_user(str(usuario.id))

            return {"detail": "Profesor eliminado definitivamente"}
        
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, f"Error al eliminar profesor: {str(e)}")
        
