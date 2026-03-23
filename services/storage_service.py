import os
from uuid import uuid4
from infrastructure.storage import upload_file_to_storage, generate_signed_url

class StorageService:

    @staticmethod 
    def generar_ruta_publicacion(publicacion_id, tipo, filename):
        extension = os.path.splitext(filename)[1]
        nombre_storage = f"{uuid4()}{extension}"

        if tipo == "tarea":
            carpeta = f"tareas/{publicacion_id}"
        else:
            carpeta = f"material/{publicacion_id}"

        return f"{carpeta}/{nombre_storage}"

    @staticmethod
    def generar_ruta_entrega(publicacion_id, alumno_id, filename):
        extension = os.path.splitext(filename)[1]
        nombre_storage = f"{uuid4()}{extension}"

        return f"entregas/{publicacion_id}-{alumno_id}/{nombre_storage}"

    @staticmethod
    def subir(ruta_storage, file):
        upload_file_to_storage(ruta_storage, file)
    
    @staticmethod
    def generar_url_firmada(ruta_storage: str, expires_in: int = 3600):
        if not ruta_storage:
            raise ValueError("Ruta de storage inválida")

        return generate_signed_url(ruta_storage, expires_in)