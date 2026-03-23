# infrastructure/storage.py
from fastapi import UploadFile
from uuid import uuid4
from core.config import settings
from infrastructure.supabase import supabase_admin

def upload_avatar_to_storage(file: UploadFile, user_id: str, bucket_name: str = "fotos_perfil") -> str:
    """
    Sube una foto de perfil al almacenamiento de Supabase.
    Args:
        supabase_admin: La instancia del cliente de Supabase con permisos administrativos.
        file (UploadFile): El archivo de imagen que se desea subir.
        user_id (str): El ID del usuario al que pertenece la foto de perfil.
        bucket_name (str): El nombre del bucket en Supabase donde se almacenará la foto. Por defecto es "fotos_perfil".
    Returns:
        str: La ruta interna del archivo subido en el bucket de Supabase.
    """
    if file.content_type not in settings.ALLOWED_TYPES:
        raise ValueError("Formato de imagen no permitido")

    extension = file.filename.split(".")[-1].lower()
    filename = f"usuarios/{user_id}/{uuid4().hex}.{extension}"

    contents = file.file.read()

    response = supabase_admin.storage.from_(bucket_name).upload(filename, contents,{"content-type": file.content_type})

    if hasattr(response, "error") and response.error:
        raise Exception(f"Error al subir avatar: {response.error}")

    return filename

def delete_old_avatar(avatar_path: str, bucket_name: str = "fotos_perfil"):
    """
    Elimina una foto de perfil anterior del almacenamiento de Supabase dado su URL pública.
    Args:
        supabase: La instancia del cliente de Supabase.
        public_url (str): La URL pública de la foto de perfil que se desea eliminar.
        bucket_name (str): El nombre del bucket en Supabase donde se almacenan las fotos de perfil. Por defecto es "fotos_perfil".
    """
    try:
        supabase_admin.storage.from_(bucket_name).remove([avatar_path])
    except Exception as e:
        raise Exception(f"Error al eliminar avatar: {e}")

def upload_file_to_storage(path: str, file):
    """
    Sube un archivo al almacenamiento de Supabase en la ruta especificada.
    Args:
        path (str): La ruta dentro del bucket de Supabase donde se desea almacenar el archivo, por ejemplo "publicaciones/{publicacion_id}/archivo.pdf".
        file: El archivo que se desea subir, generalmente un objeto UploadFile de FastAPI.
    """
    content = file.file.read()

    response = supabase_admin.storage.from_(settings.BUCKET_NAME).upload(path, content, {"content-type": file.content_type,
                                            "x-upsert": "false"})
    if hasattr(response, "error") and response.error:
        raise Exception(f"Error al subir archivo: {response.error}")
    
    

def generate_signed_url(path: str, expires_in: int = 3600):
    """
    Genera una URL temporal firmada para acceder a un archivo privado.
    expires_in: segundos de validez
    """
    response = supabase_admin.storage.from_(settings.BUCKET_NAME).create_signed_url(path, expires_in)
    if hasattr(response, "error") and response.error:
        raise Exception("Error al generar signed URL")

    return response.get("signedURL")