Proyecto: Gestión de Alumnos con FastAPI y SQLModel

Este proyecto es una API REST para gestionar alumnos utilizando FastAPI y SQLModel (con soporte para PostgreSQL / Supabase).
Permite crear, leer, actualizar y eliminar alumnos, con validaciones de datos (nombre, apellido y edad).

📁 Estructura del proyecto
project/
│
├─ app/
│  ├─ main.py               # Archivo principal de FastAPI
│  ├─ database.py           # Conexión a la base de datos
│  ├─ models/
│  │  ├─ alumno.py          # Modelos SQLModel y Pydantic (AlumnoDB, AlumnoCreate, AlumnoUpdate)
│  ├─ routers/
│  │  ├─ alumno.py          # Endpoints CRUD de alumnos
│  └─ __init__.py
│
├─ requirements.txt         # Dependencias del proyecto
└─ README.md

⚡ Tecnologías utilizadas

Python 3.10+

FastAPI

SQLModel

Pydantic

PostgreSQL / Supabase

Uvicorn (servidor ASGI)

🔧 Instalación

Clonar el repositorio:

git clone https://github.com/tu_usuario/tu_repo.git
cd tu_repo


Crear entorno virtual e instalar dependencias:

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt


Configurar conexión a la base de datos en database.py:

DATABASE_URL = "postgresql://usuario:password@host:puerto/dbname"


Inicializar la base de datos (si se usa SQLModel para crear tablas automáticamente):

from database import engine
from models.alumno import AlumnoDB, SQLModel

SQLModel.metadata.create_all(engine)

🚀 Ejecutar la API
uvicorn app.main:app --reload


La API estará disponible en http://127.0.0.1:8000.

📝 Endpoints disponibles
1. Crear alumno (POST)

URL: /alumnos/

Body JSON:

{
  "nombre": "Juan",
  "apellido": "Perez",
  "edad": 20
}


Validaciones:

Nombre y apellido solo letras, sin espacios ni vacíos.

Edad entre 3 y 100 años.

Respuesta: Objeto AlumnoDB con id generado.

2. Leer todos los alumnos (GET)

URL: /alumnos/

Respuesta: Lista de todos los alumnos.

3. Leer alumno por ID (GET)

URL: /alumnos/{alumno_id}

Respuesta: Objeto AlumnoDB correspondiente.

4. Actualizar alumno completo (PUT)

URL: /alumnos/{alumno_id}

Body JSON: Igual que POST.

Respuesta: Objeto AlumnoDB actualizado.

5. Actualizar alumno parcialmente (PATCH)

URL: /alumnos/{alumno_id}

Body JSON: Campos opcionales a actualizar:

{
  "edad": 25
}


Respuesta: Objeto AlumnoDB actualizado.

6. Eliminar alumno (DELETE)

URL: /alumnos/{alumno_id}

Respuesta: Mensaje de confirmación:

{
  "ok": true,
  "mensaje": "Alumno eliminado"
}

📌 Validaciones

nombre y apellido:

Solo letras, sin espacios, no vacío.

edad:

Número entero entre 3 y 100.

Si alguna validación falla, la API devuelve 422 Unprocessable Entity con el mensaje correspondiente.

🔗 Recursos adicionales

Documentación FastAPI

Documentación SQLModel

Pydantic Validators

