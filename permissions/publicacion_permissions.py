from models.enums import PerfilUsuario,TipoPublicacion,EstadosEntregas
from models.usuario import Usuario
from models.publicacion import Publicacion
from models.entrega import Entrega
from repositories.curso_profesor_repository import CursoProfesorRepository
from repositories.curso_alumno_repository import CursoAlumnoRepository
from datetime import datetime, timezone


class PublicacionPermission:

    def __init__(self,curso_profesor_repo: CursoProfesorRepository,
                    curso_alumno_repo: CursoAlumnoRepository):
        
        self.curso_profesor_repo = curso_profesor_repo
        self.curso_alumno_repo = curso_alumno_repo

    def puede_ver_publicacion(self, usuario: Usuario, publicacion: Publicacion) -> bool:

        if usuario.perfil == PerfilUsuario.admin:
            return True

        # Si está inactiva solo el creador puede verla
        if not publicacion.activa and publicacion.profesor_id != usuario.id:
            return False

        if usuario.perfil == PerfilUsuario.profesor:
            return True

        if usuario.perfil == PerfilUsuario.alumno:
            inscripcion = self.curso_alumno_repo.esta_inscripto(
                publicacion.materia_curso_id,
                usuario.id
            )
            return bool(inscripcion)

        return False

    def puede_crear_publicacion(self, usuario: Usuario, materia_curso_id):

        if usuario.perfil != PerfilUsuario.profesor:
            return False

        relacion = self.curso_profesor_repo.esta_asignado(
            materia_curso_id,
            usuario.id
        )

        return bool(relacion)
    def puede_actualizar_publicacion(self, usuario: Usuario, publicacion: Publicacion):

        if usuario.perfil != PerfilUsuario.profesor:
            return False

        if not publicacion.activa:
            return False

        return publicacion.profesor_id == usuario.id
    
    def puede_eliminar_publicacion(self, usuario:Usuario, publicacion):

        if usuario.perfil == PerfilUsuario.admin:
            return True

        if usuario.perfil == PerfilUsuario.profesor:
            return publicacion.profesor_id == usuario.id

        return False
    
    def puede_subir_archivo(self, usuario: Usuario, publicacion: Publicacion) -> bool:

        if usuario.perfil != PerfilUsuario.profesor:
            return False

        # no se pueden subir archivos a avisos
        if publicacion.tipo == TipoPublicacion.aviso:
            return False

        # debe estar asignado a la materia
        relacion = self.curso_profesor_repo.esta_asignado(publicacion.materia_curso_id,
                                                        usuario.id)

        return bool(relacion)

    def puede_entregar_tarea(self, usuario: Usuario, publicacion: Publicacion) -> bool:

        # Solo alumnos
        if usuario.perfil != PerfilUsuario.alumno:
            return False

        # Debe ser tipo tarea
        if publicacion.tipo != TipoPublicacion.tarea:
            return False

        # No debe estar vencida
        if publicacion.fecha_entrega and datetime.now(timezone.utc) > publicacion.fecha_entrega:
            return False

        # Debe estar inscripto
        relacion = self.curso_alumno_repo.esta_inscripto(publicacion.materia_curso_id,
                                                        usuario.id)

        return bool(relacion)
    
    def puede_corregir_entrega(self, usuario: Usuario, entrega: Entrega, publicacion: Publicacion):

        if usuario.perfil != PerfilUsuario.profesor:
            return False

        if entrega.estado == EstadosEntregas.corregido:
            return False

        relacion = self.curso_profesor_repo.esta_asignado(publicacion.materia_curso_id,
                                                        usuario.id)

        return bool(relacion)
    
    def puede_descargar(self,usuario: Usuario,
                        publicacion: Publicacion,
                        entrega: Entrega | None = None):

        if usuario.perfil == PerfilUsuario.admin:
            return True

        if usuario.perfil == PerfilUsuario.profesor:
            relacion = self.curso_profesor_repo.esta_asignado(publicacion.materia_curso_id,
                                                                usuario.id)
            return bool(relacion)

        if usuario.perfil == PerfilUsuario.alumno:

            inscripcion = self.curso_alumno_repo.esta_inscripto(publicacion.materia_curso_id,
                                                                usuario.id)

            if not inscripcion:
                return False

            # si es archivo de entrega, solo puede ver el suyo
            if entrega and entrega.alumno_id != usuario.id:
                return False

            return True

        return False
    
""" "ALUMNO
eyJhbGciOiJIUzI1NiIsImtpZCI6IjFneWtoTjk4cVV6SHV4disiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2Zja2R6Y2tkemxiZHFwYmllcWl3LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJjNjVjZTgzYS02OTFjLTRmNzItYmM3ZC00OWIyOWZlOWZmZWEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc0Mjk1MzA5LCJpYXQiOjE3NzQyOTE3MDksImVtYWlsIjoidXNlcjFAZXhhbXBsZS5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc3NDI5MTcwOX1dLCJzZXNzaW9uX2lkIjoiN2M3MTk4MTEtMzFmZS00ZTBhLWI0ZmQtMDhiZDQyMTlhNWUzIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.V2MHLNML4aXq7-dFh9yitCyhUq72iTG-fmmZQHKE03c
" 
"""
"""
PROFESOR 
"eyJhbGciOiJIUzI1NiIsImtpZCI6IjFneWtoTjk4cVV6SHV4disiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2Zja2R6Y2tkemxiZHFwYmllcWl3LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJjMWY4YWM0ZC05Nzg3LTQ1N2UtYWJlOC05OTQ2Mjk1ZTI1NTAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc0Mjk1NDY0LCJpYXQiOjE3NzQyOTE4NjQsImVtYWlsIjoidXNlcjJAZXhhbXBsZS5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc3NDI5MTg2NH1dLCJzZXNzaW9uX2lkIjoiYTg5MDBiOTctZmI2MC00MmM4LWE4OWQtYmE3MjgyMWJlYWEyIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.K1lNdRwJwgqb-D6SCMCncqNTHi9X5ChF5p7kg6PC99Q" """