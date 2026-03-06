```
🏫 API REST de Gestion De Alumnos con FAST API, SQLModel Python 3.12 , Supabase PostgreSQL. Permite crear, leer, actualizar y eliminar registros, con validaciones de datos.

📁 Estructura del proyecto
api-colegio/
│  └─ models/
│  │  ├─ alumno.py                 # Modelos SQLModel (Alumno)
│  │  ├─ archivo_publicacion.py    # Modelos SQLModel (ArchivosPublicacion)
│  │  ├─ curso_alumno.py           # Modelos SQLModel (CursoAlumno)
│  │  ├─ curso_profesor.py         # Modelos SQLModel (CursoProfesor)
│  │  ├─ curso.py                  # Modelos SQLModel (Curso)
│  │  ├─ entrega.py                # Modelos SQLModel (Entrega)
|  |  ├─ enums.py                  # Enumerados Enum (PerfilUsuario, EstadosAlumno, TiposContrato)
|  |  ├─ historial_contrasenas.py  # Modelos SQLModel  (HistorialContrasenas)
│  │  ├─ materia_curso.py          # Modelos SQLModel (MateriaCurso)
│  │  ├─ materia.py                # Modelos SQLModel (Materia)
|  |  ├─ profesor.py               # Modelos SQLModel  (Profesor)
│  │  ├─ publicacion.py            # Modelos SQLModel (Publicacion)
│  │  ├─ tarea_entregada.py        # Modelos SQLModel (TareaEntregada)
|  |  ├─ usuario.py                # Modelos SQLModel  (Usuario)
|  └─ routers/
|  |  ├─ alumnos.py                # Contiene los endpoints (get_alumno, get_alumnos, get_alumno_en_curso, asignar_curso_alumno, delete_alumno_de_curso, delete_alumno, update_alumno)
|  |  ├─ auth.py                   # Contiene los endpoints  (register_alumno, register_profesor, verificar_credenciales, me, upload_avatar, reset_password)
|  |  ├─ cursos.py                 # Contiene los endpoints  (get_cursos, create_curso, get_curso, update_curso, delete_curso)
|  |  ├─ materia_curso.py          # Contiene los endpoints  (get_materia_curso, create_materia_curso, delete_materia_curso)
|  |  ├─ materias.py               # Contiene los endpoints  (get_materias, create_materia, get_materia, update_materia, delete_materia)
|  |  ├─ profesores.py             # Contiene los endpoints  (get_profesores, get_profesor, get_profesor_en_materia_curso, asignar_curso_y_materia_profesor, delete_profesor_de_curso_materia, delete_profesor, update_profesor)
|  |  ├─ publicaciones.py          # Contiene los endpoints  (leer_datos_publicacion, actualizar_publicacion, eliminar_publicacion, leer_archivos_tarea_o_materia_publicacion,crear_publicacion, subir_material_o_tarea, entregar_tarea, corregir_entrega, descargar_archivo)
|  └─ schemas/
|  |  ├─ alumno.py                 # Contiene los BaseModel del alumno  (AlumnoOut, AlumnoOutFull, AlumnoUpdate)
|  |  ├─ archivo_publicacion.py    # Contiene los BaseModel de archivoPublicacion  (ArchivoPublicacionOut)
|  |  ├─ auth.py                   # Contiene los BaseModel del auth para registrar y dar de alta (RegisterBase, RegisterAlumno, RegisterProfesor, RegisterAdmin, LoginSchema, ResetPasswordSchema)
|  |  ├─ curso.py                  # Contiene los BaseModel de los cursos (CursoOut, CursoCreate, CursoUpdate)
|  |  ├─ entregas.py               # Contiene los BaseModel de las entregas (CorreccionCreate)
|  |  ├─ materia_curso.py          # Contiene los BaseModel de materia_curso  (CursoBasic, MateriaBasic, MateriaCursoOutStandar, MateriaCursoOutFull, MateriaCursoCreate)
|  |  ├─ materia.py                # Contiene los BaseModel de las materias (MateriaOut, MateriaCreate, MateriaUpdate)
|  |  ├─ me.py                     # Contiene los BaseModel para ver que usuario esta logueado  (MeResponse)
|  |  ├─ profesor.py               # Contiene los BaseModel del profesor  (ProfesorOut, ProfesorOutFull, ProfesorUpdate)
|  |  ├─ publicacion.py            # Contiene los BaseModel de las publicaciones (PublicacionOut, PublicacionCreate, PublicacionUpdate)
|  |  ├─ usuario.py                # Contiene los BaseModel  del usuario  (UsuarioOut, UsuarioUpdate)
|  ├─ venv                         # Esta carpeta lo que hace es tener todas las librerias que se usan en el proyecto, no se sube al github porque no es necesario gastar espacio en eso
│  ├─ .dockerignore                # Ignora los archivos que no se usan en docker
|  ├─ .env                         # Este Archivo que contiene las variables de entorno para acceder a la base de datos, etc este archivo no se sube
|  ├─ .gitignore                   # Este Archivo que ignora los archivos temporales o que no queramos que se uban a github
|  ├─ configuration.py             # Este Archivo de python contiene todo lo necesario para manejar las conexiones con la base de datos, manejar las sesiones dentro de Supabase y verificar los JWT
│  ├─ Dockerfile                   # Este archivo es el contenedor de todo nuestro proyecto para poder subirlo a un host para que se use sin necesidad de estar en el local
│  ├─ main.py                      # Este archivo contiene todo lo necesario para arrancar la api con sus routers, middlewares
|  ├─ pasos_para_correr_API.txt    # Pasos para correr la api en el local y probar en la maquina propia
|  ├─ README.md                    # Documentación de todo el proyecto, lo  que hace cada endpoint esta en "https://api-colegio-baig.onrender.com/docs" o Documentacion Proyecto local "http://127.0.0.1:8000/docs" si lo corremos local
|  ├─ requirements.txt             # Dependencias para instalar en el proyecto
|  ├─ runtime.txt                  # Se usa para forzar a render a usar la version que le pongas, pero al usar Docker ya no hace falta
|  ├─ supabase-schema-fckdzckdzlbdqpbieqiw.png es la imagen de como esta organizada la base datos


⚡ Tecnologías utilizadas
- Python 3.10+
- FastAPI
- SQLModel
- Pydantic
- PostgreSQL / Supabase
- Uvicorn (servidor ASGI)
🔗 Recursos adicionales
- Documentación FastAPI
- Documentación SQLModel
- Pydantic Validators
```
