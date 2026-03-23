from pydantic import BaseModel , Field, field_validator
from pydantic.config import ConfigDict
from uuid import UUID
from datetime import date,datetime
from models.enums import EstadosAlumno, EstadosAlumnosEnCurso, Turnos, PerfilUsuario
from schemas.usuario import UsuarioUpdate, UsuarioOut
from typing import Optional
import re
# Este schema se utiliza para la creación de un nuevo alumno, donde se requieren 
# los campos nombre, apellido y edad, mientras que el perfil es opcional.
class AlumnoOut(BaseModel): # Lo que sale al GET, DATOS DEL ALUMNO, SE USA PARA MOSTRAR LOS DATOS BASICOS DEL ALUMNO EN EL PERFIL DEL ALUMNO
    id: UUID
    legajo: Optional[str]
    fecha_ingreso: Optional[date]
    estado: EstadosAlumno
    observaciones: Optional[str]
    activo: bool
    
    class Config:
        from_attributes = True
    

class AlumnoOutFull(BaseModel): # Lo que sale al GET con toda la info del usuario, se utiliza para mostrar el perfil del alumno
    id: UUID
    legajo: str | None
    fecha_ingreso: date | None
    estado: EstadosAlumno
    observaciones: str | None
    activo: bool

    usuario: UsuarioOut
    model_config = ConfigDict(from_attributes=True)

class AlumnoUpdate(BaseModel): # Lo que entra al PUT, todos los campos son opcionales porque el alumno puede querer actualizar solo algunos, se utiliza para que el alumno pueda actualizar su perfil desde la app
    legajo: Optional[str] = Field(default=None,min_length=2,max_length=10,description="Legajo del alumno")
    fecha_ingreso: Optional[date] = None
    estado: Optional[EstadosAlumno] = None
    observaciones: Optional[str] = Field(default=None,max_length=255)
    activo: Optional[bool] = None

    @field_validator("legajo")
    @classmethod
    def validar_legajo(cls, value: str | None):
        if value is None:
            return value

        value = value.strip().upper()

        if not re.match(r"^[A-Z0-9]+$", value):
            raise ValueError("El legajo solo puede contener letras y números")

        if not re.search(r"[A-Z]", value):
            raise ValueError("El legajo debe contener al menos una letra")

        if not re.search(r"[0-9]", value):
            raise ValueError("El legajo debe contener al menos un número")

        return value


    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, value):
        if value is None:
            return value

        if value > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")

        return value
    
    @field_validator("observaciones")
    @classmethod
    def validar_observaciones(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Las observaciones no pueden estar vacías")

        return value
class AlumnoFullUpdate(BaseModel): # Lo que entra al PUT, todos los campos son opcionales porque el alumno puede querer actualizar solo algunos
    alumno: AlumnoUpdate
    usuario: UsuarioUpdate

#Seccion de alumno en curso
class UsuarioBasic(BaseModel): # DATOS DE LA TABLA USAARIO, LO USAMOS PARA TENER EL NOMBRE O APELLIDO O EDAD
    id: UUID
    nombre: str
    apellido: str
    edad: int
    perfil: PerfilUsuario
    ruta_foto: Optional[str] = None
    fecha_registro: datetime

    class Config:
        from_attributes = True

class AlumnoBasic(BaseModel): # DATOS DE LA TABLA ALUMNO, LO USAMOS PARA TENER EL LEGAJO O FECHA DE INGRESO O ESTADO, 
    id: UUID
    legajo: Optional[str]
    fecha_ingreso: Optional[date]
    estado: EstadosAlumno
    observaciones: Optional[str]
    activo: bool
    usuario: UsuarioBasic | None = None
    
    class Config:
        from_attributes = True
class AlumnoEnCursoBasic(BaseModel): # LO MANDAMOS EN EL ROUTER Y LO USAMOS PARA CREAR Y OBTENER LOS DATOS BASICOS DE LA TABALA ALUMNO_EN_CURSO
    id: UUID
    alumno_id: UUID
    curso_id: UUID
    ciclo_lectivo: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: EstadosAlumnosEnCurso
    class Config:
        from_attributes = True

class CursoBasic(BaseModel): # LO USAMOS PARA MOSTRAR LOS DATOS BASICOS DEL CURSO EN EL PERFIL DEL ALUMNO, NO ES NECESARIO MOSTRAR TODOS LOS DATOS DEL CURSO
    id: UUID
    nombre: str
    turno: Turnos
    nivel: str

    class Config:
        from_attributes = True

class AlumnoCursoOutFull(BaseModel): # LO USAMOS PARA MOSTRAR LA INFORMACION COMPLETA DEL ALUMNO EN CURSO, INCLUYENDO LOS DATOS DEL CURSO Y LOS DATOS DEL ALUMNO
    id: UUID
    ciclo_lectivo: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: EstadosAlumnosEnCurso

    curso: CursoBasic
    alumno: AlumnoBasic

    class Config:
        from_attributes = True

class AlumnoEnCursoCreate(BaseModel):   # SOLO SE USA EN LA FUNCION DE POST COMO DATA,  LO USAMOS PARA CREAR UN NUEVO ALUMNO EN CURSO, SE REQUIEREN LOS CAMPOS ALUMNO_ID, 
                                        # CURSO_ID Y CICLO_LECTIVO, LOS DEMAS CAMPOS SON OPCIONALES
    alumno_id: UUID
    curso_id: UUID
    ciclo_lectivo: int = Field(..., ge=2000, le=2100)
    fecha_inicio: datetime  = Field(default_factory=datetime.utcnow)
    fecha_fin: Optional[datetime] = None
    estado: EstadosAlumnosEnCurso = EstadosAlumnosEnCurso.cursando

    @field_validator("ciclo_lectivo")
    def validar_anio(cls, value):
        if value < 2000:
            raise ValueError("El ciclo lectivo debe ser un año válido")
        return value
    
    
    @field_validator("fecha_inicio", mode="before")
    @classmethod
    def set_fecha_actual_si_null(cls, value):
        if value is None:
            return datetime.utcnow()
        return value