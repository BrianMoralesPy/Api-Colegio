from fastapi import HTTPException
from sqlmodel import Session
from uuid import UUID

from schemas.alumno import AlumnoOutFull,AlumnoUpdate
from schemas.usuario import UsuarioUpdate
from infrastructure.supabase import supabase_admin

from repositories.alumno_repository import AlumnoRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.historial_repository import HistorialContrasenasRepository

class AlumnoService:
    def __init__(self, session:Session):
        self.session = session
        self.alumno_repo = AlumnoRepository(session)
        self.usuario_repo = UsuarioRepository(session)
        self.historial_repo = HistorialContrasenasRepository(session)
    
    def get_alumnos(self) -> list[AlumnoOutFull]:
        """
        Obtener la lista de todos los alumnos.

        Este Metodo devuelve todos los alumnos registrados en el sistema junto con
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
            alumnos = self.alumno_repo.get_all()
            return [AlumnoOutFull.model_validate(a) for a in alumnos]

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(500, "Error al obtener alumnos")
        
    def get_alumno(self, alumno_id: UUID) -> AlumnoOutFull:
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
            alumno = self.alumno_repo.get_by_id(alumno_id)
            if not alumno:
                raise HTTPException(404, "Alumno no encontrado")

            usuario = self.usuario_repo.get_by_id(alumno.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")

            return AlumnoOutFull.model_validate(alumno)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error al obtener alumno: {str(e)}")
        
    def update_alumno(self, alumno_id: UUID, alumno_data: AlumnoUpdate,
                        usuario_data: UsuarioUpdate) -> dict:
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
            alumno = self.alumno_repo.get_by_id(alumno_id)
            if not alumno:
                raise HTTPException(404, "Alumno no encontrado")

            usuario = self.usuario_repo.get_by_id(alumno.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")

            # Actualizar Alumno
            for key, value in alumno_data.model_dump(exclude_unset=True).items():
                setattr(alumno, key, value)

            # Actualizar Usuario
            for key, value in usuario_data.model_dump(exclude_unset=True).items():
                setattr(usuario, key, value)

            self.session.commit()
            return {"detail": "Alumno actualizado correctamente"}

        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, f"Error al actualizar alumno: {str(e)}")

    def delete_alumno(self, alumno_id: UUID) -> dict:
        """
        Eliminar definitivamente un alumno del sistema.

        Este Metodo elimina:
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
        try:
            alumno = self.alumno_repo.get_by_id(alumno_id)
            if not alumno:
                raise HTTPException(404, "Alumno no encontrado")

            usuario = self.usuario_repo.get_by_id(alumno.id)
            if not usuario:
                raise HTTPException(500, "Usuario inconsistente")

            # Borrar historial
            self.historial_repo.delete_by_user_id(alumno.id)

            # Borrar alumno y usuario
            self.alumno_repo.delete(alumno)
            self.usuario_repo.delete(usuario)

            self.session.commit()

            # Borrar en Supabase Auth (después del commit)
            supabase_admin.auth.admin.delete_user(str(usuario.id))

            return {"detail": "Alumno eliminado definitivamente"}

        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, f"Error al eliminar alumno: {str(e)}")
    
