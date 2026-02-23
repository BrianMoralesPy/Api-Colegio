from pydantic import BaseModel, EmailStr,field_validator,Field
from models.enums import PerfilUsuario
import re
# Este schema se utiliza para la creación de un nuevo alumno, donde se requieren 
# los campos nombre, apellido y edad, mientras que el perfil es opcional.
class RegisterBase(BaseModel): # Lo que entra al POST, se utiliza para registrar un nuevo usuario, ya sea alumno, profesor o admin
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    edad: int
    foto_url: str | None = None

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[0-9]", value):
            raise ValueError("La contraseña debe tener al menos un número")
        return value

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Solo se permiten letras")
        return value.strip().title()

    @field_validator("edad")
    @classmethod
    def validar_edad(cls, value: int) -> int:
        if value < 5 or value > 100:
            raise ValueError("Edad mínima requerida: 6")
        return value

class RegisterAlumno(RegisterBase):
    perfil: PerfilUsuario = PerfilUsuario.alumno

class RegisterProfesor(RegisterBase):
    perfil: PerfilUsuario = PerfilUsuario.profesor

class RegisterAdmin(RegisterBase):
    perfil: PerfilUsuario = PerfilUsuario.admin

class LoginSchema(BaseModel): # Lo que entra al POST, se utiliza para iniciar sesión
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La contraseña es obligatoria")
        return value

class ResetPasswordSchema(BaseModel): # Lo que entra al POST, se utiliza para restablecer la contraseña directamente
    user_id: str = Field(..., description="UUID del usuario")
    new_password: str = Field(...,min_length=8)
