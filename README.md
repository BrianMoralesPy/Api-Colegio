```
🏫 API REST de Gestion De Alumnos con FAST API, SQLModel Python 3.12 , Supabase PostgreSQL. Permite crear, leer, actualizar y eliminar registros, con validaciones de datos.

📁 Estructura del proyecto
api-colegio/
|  └─ core/
|  |  └─ security/
|  |  |  ├─ auth.py 
|  |  |  ├─ hashing.py
|  |  |  ├─ permissions.py
|  |  ├─ config.py
|  |  ├─ databse.py
│  └─ infrastructure/
|  |  ├─ storage.py
|  |  ├─ supabase.py
│  └─ models/
│  │  ├─ alumno.py                 
│  │  ├─ archivo_publicacion.py    
│  │  ├─ curso_alumno.py           
│  │  ├─ curso_profesor.py         
│  │  ├─ curso.py                  
│  │  ├─ entrega.py                
|  |  ├─ enums.py                  
|  |  ├─ historial_contrasenas.py  
│  │  ├─ materia_curso.py          
│  │  ├─ materia.py                
|  |  ├─ profesor.py               
│  │  ├─ publicacion.py            
│  │  ├─ tarea_entregada.py        
|  |  ├─ usuario.py 
│  └─ permissions/
│  |  ├─ publicacion_permissions.py
│  └─ repositories/
│  │  ├─ alumno_repository.py                 
│  │  ├─ archivo_publicacion_repository.py    
│  │  ├─ curso_alumno_repository.py           
│  │  ├─ curso_profesor_repository.py         
│  │  ├─ curso_repository.py                  
│  │  ├─ entrega_repository.py                                  
|  |  ├─ historial_repository.py  
│  │  ├─ materia_curso_repository.py          
│  │  ├─ materia_repository.py                
|  |  ├─ profesor_repository.py               
│  │  ├─ publicacion_repository.py            
│  │  ├─ tarea_entregada_repository.py        
|  |  ├─ usuario_repository.py                
|  └─ routers/
|  |  ├─ alumnos_en_curso.py  
|  |  ├─ alumnos.py                
|  |  ├─ auth.py                   
|  |  ├─ cursos.py
|  |  ├─ health.py                  
|  |  ├─ materia_curso.py          
|  |  ├─ materias.py
|  |  ├─ profesores_en_curso.py                
|  |  ├─ profesores.py             
|  |  ├─ publicaciones.py          
|  └─ schemas/
|  |  ├─ alumno.py                 
|  |  ├─ archivo_publicacion.py    
|  |  ├─ auth.py                   
|  |  ├─ curso.py                  
|  |  ├─ entregas.py               
|  |  ├─ materia_curso.py          
|  |  ├─ materia.py                
|  |  ├─ me.py                     
|  |  ├─ profesor.py              
|  |  ├─ publicacion.py            
|  |  ├─ usuario.py
|  └─ services/
|  |  ├─ alumno_service.py                 
|  |  ├─ auth_service.py    
|  |  ├─ curso_alumno_service.py                   
|  |  ├─ curso_profesor_service.py                  
|  |  ├─ curso_service.py               
|  |  ├─ materia_curso_service.py          
|  |  ├─ materia_service.py                
|  |  ├─ profesor_service.py                     
|  |  ├─ publicacion_service.py              
|  |  ├─ storage_service.py                           
|  ├─ venv                         
│  ├─ .dockerignore                
|  ├─ .env                        
|  ├─ .gitignore                               
│  ├─ Dockerfile                   
│  ├─ main.py                        
|  ├─ README.md                     
|  ├─ requirements.txt             



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

📷 Documentación visual de endpoints
Las siguientes capturas corresponden a la documentación automática generada por FastAPI Swagger UI.

Documentación online:
https://api-colegio-baig.onrender.com/docs

Documentación local:
http://127.0.0.1:8000/docs
```



- Endpoints relacionados con la gestión de alumnos.

![GET get_alumnos](imgs_readme/alumnos/get_alumnos.png)

![GET get_alumno](imgs_readme/alumnos/get_alumno.png)

![GET get_alumno_en_curso](imgs_readme/alumnos/get_alumno_en_curso.png)

![POST asignar_curso_alumno](imgs_readme/alumnos/asignar_curso_alumno.png)

![PUT update_alumno](imgs_readme/alumnos/update_alumno.png)

![DELETE delete_alumno](imgs_readme/alumnos/delete_alumno.png)

![DELETE delete_alumno_de_curso](imgs_readme/alumnos/delete_alumno_de_curso.png)

- Endpoints relacionados con la gestión Autentificacion, Creacion de Cuenta, e Inicio de Sesion para los roles.

![GET obtener_datos_usuario_logueado](imgs_readme/auth/obtener_datos_usuario_logueado.png)

![POST recuperar_contrasenia](imgs_readme/auth/recuperar_contrasenia.png)

![POST register_alumno](imgs_readme/auth/register_alumno.png)

![POST register_profesor](imgs_readme/auth/register_profesor.png)

![PUT subir_foto_perfil_o_modificar](imgs_readme/auth/subir_foto_perfil_o_modificar.png)

![POST verificar_credenciales](imgs_readme/auth/verificar_credenciales.png)

- Endpoints relacionados con la gestión de cursos en el sistema

![GET get_cursos](imgs_readme/cursos/get_cursos.png)

![GET get_curso](imgs_readme/cursos/get_curso.png)

![POST create_curso](imgs_readme/cursos/create_curso.png)

![PUT update_curso](imgs_readme/cursos/update_curso.png)

![DELETE delete_curso](imgs_readme/cursos/delete_curso.png)

- Endpoints relacionados con la gestión de materias en el sistema

![GET get_materias](imgs_readme/materias/get_materias.png)

![GET get_materia](imgs_readme/materias/get_materia.png)

![POST create_materia](imgs_readme/materias/create_materia.png)

![PUT update_materia](imgs_readme/materias/update_materia.png)

![DELETE delete_materia](imgs_readme/materias/delete_materia.png)

- Endpoints relacionados con la gestión de la relacion materia_curso en el sistema

![GET get_materias_curso](imgs_readme/materiasCurso/get_materias_curso.png)

![POST create_materia_curso](imgs_readme/materiasCurso/create_materia_curso.png)

![DELETE delete_materia_curso](imgs_readme/materiasCurso/delete_materia_curso.png)

- Endpoints relacionados con la gestión de profesores.

![GET get_profesores](imgs_readme/profesores/get_profesores.png)

![GET get_profesor](imgs_readme/profesores/get_profesor.png)

![GET get_profesor_en_curso_materia](imgs_readme/profesores/get_profesor_en_curso_materia.png)

![POST asignar_curso_y_materia_profesor](imgs_readme/profesores/asignar_curso_y_materia_profesor.png)

![PUT update_profesor](imgs_readme/profesores/update_profesor.png)

![DELETE delete_profesor](imgs_readme/profesores/delete_profesor.png)

![DELETE delete_profesor_de_curso_materia](imgs_readme/profesores/delete_profesor_de_curso_materia.png)

- Endpoints relacionados con la gestión de publicaciones, entregas, subidas de archivos.

![GET leer_datos_publicacion](imgs_readme/publicaciones/leer_datos_publicacion.png)

![GET leer_archivos_tarea_o_material](imgs_readme/publicaciones/leer_archivos_tarea_o_material.png)

![GET descargar_archivo](imgs_readme/publicaciones/descargar_archivo.png)

![POST crear_publicacion](imgs_readme/publicaciones/crear_publicacion.png)

![POST entregar_tarea_y_subir_su_archivo](imgs_readme/publicaciones/entregar_tarea_y_subir_su_archivo.png)

![POST subir_archivos_material_o_tarea](imgs_readme/publicaciones/subir_archivos_material_o_tarea.png)

![PUT actualizar_publicacion](imgs_readme/publicaciones/actualizar_publicacion.png)

![PUT coreccion_tarea](imgs_readme/publicaciones/coreccion_tarea.png)

![DELETE eliminar_publicacion](imgs_readme/publicaciones/eliminar_publicacion.png)
