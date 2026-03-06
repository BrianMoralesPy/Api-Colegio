from fastapi import APIRouter, Depends, HTTPException
from services.configuration import get_session,supabase_admin,require_role
from sqlmodel import Session,select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from uuid import UUID
from models.materia_curso import MateriaCurso
from models.enums import PerfilUsuario
from schemas.materia_curso import MateriaCursoCreate, MateriaCursoOutFull, MateriaCursoOutStandar
router = APIRouter(prefix="/materias_curso", tags=["MateriasCurso"])

@router.post("/", response_model=MateriaCursoOutStandar)
def create_materia_curso(data: MateriaCursoCreate, session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))) -> MateriaCursoOutStandar:
    """
    Crear una relación entre una materia y un curso.

    Este endpoint permite asignar una **materia** a un **curso** para un
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
        # Validación preventiva (opcional pero recomendable) 
        statement = select(MateriaCurso).where(MateriaCurso.curso_id == data.curso_id,
                                                MateriaCurso.materia_id == data.materia_id,
                                                MateriaCurso.ciclo_lectivo == data.ciclo_lectivo)

        existing = session.exec(statement).first() # Verificar si ya existe una relación con el mismo curso, materia y ciclo lectivo

        if existing:
            raise HTTPException(status_code=400, detail="Esta materia ya está asignada a ese curso en ese ciclo lectivo")

        nueva_relacion = MateriaCurso(**data.model_dump()) # Crear la nueva relación utilizando el modelo de datos

        session.add(nueva_relacion) # Agregar la nueva relación a la sesión
        session.commit() # Intentar guardar los cambios en la base de datos
        session.refresh(nueva_relacion) # Refrescar el objeto para obtener el ID generado y otros campos automáticamente asignados

        return nueva_relacion

    except IntegrityError:
        session.rollback() #    Si ocurre un error de integridad (como una violación de la restricción única), revertir la transacción para mantener la consistencia de la base de datos
        raise HTTPException(status_code=400, detail="Registro duplicado")
    except HTTPException:
        raise 

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error al crear materia_curso: {str(e)}")

@router.get("/", response_model=list[MateriaCursoOutFull])
def get_materias_curso(curso_id: UUID | None = None, ciclo_lectivo: int | None = None,session: Session = Depends(get_session),
                        user=Depends(require_role(PerfilUsuario.admin))) -> list[MateriaCursoOutFull]:
    """
    Obtener las materias asignadas a cursos.
    Este endpoint devuelve la lista de relaciones **Materia-Curso** registradas
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
        # Construir la consulta base con las relaciones necesarias para evitar N+1
        statement = (select(MateriaCurso).options(selectinload(MateriaCurso.curso),selectinload(MateriaCurso.materia)))
        if curso_id:
            # Filtrar por curso_id si se proporciona
            statement = statement.where(MateriaCurso.curso_id == curso_id)
        
        if ciclo_lectivo:
            # Filtrar por ciclo_lectivo si se proporciona
            statement = statement.where(MateriaCurso.ciclo_lectivo == ciclo_lectivo)
        # Ejecutar la consulta y obtener los resultados
        materias_curso = session.exec(statement).all()
        return materias_curso   # SQLModel se encargará de convertir cada objeto MateriaCurso en MateriaCursoOutFull 
                                # gracias a la configuración de from_attributes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener materias_curso: {str(e)}")

@router.delete("/{materia_curso_id}")
def delete_materia_curso(materia_curso_id: UUID, session: Session = Depends(get_session),
                            user=Depends(require_role(PerfilUsuario.admin))) -> dict:
    """
    Eliminar una relación entre una materia y un curso.

    Este endpoint permite eliminar una relación existente entre una
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
        # Buscar la relación por su ID
        materia_curso = session.get(MateriaCurso, materia_curso_id) 

        if not materia_curso:
            raise HTTPException(status_code=404, detail="MateriaCurso no encontrada")
        session.delete(materia_curso)
        session.commit()

        return {"message": "MateriaCurso eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar materia_curso: {str(e)}")