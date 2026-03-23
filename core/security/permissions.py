# core/security/permissions.py
from fastapi import Depends, HTTPException, status
from models.enums import PerfilUsuario
from core.security.auth import get_current_user

def require_role(required_role: PerfilUsuario):
    """
    Dependencia de FastAPI que verifica si el usuario autenticado tiene el rol requerido para acceder a un endpoint específico.
    Args:        required_role (PerfilUsuario): El rol requerido para acceder al endpoint, definido en el enum PerfilUsuario.
    Returns:        function: Una función que se puede usar como dependencia en FastAPI para proteger endpoints según el rol del usuario.
    Comportamiento:        - La función interna role_checker se encarga de verificar el rol del usuario autenticado.        - Si el perfil del 
    usuario no coincide con el rol requerido, se lanza una excepción HTTP 403 Forbidden.        
    - Si el usuario tiene el rol adecuado, se devuelve la información del usuario para su uso en el endpoint protegido.
    Uso:        - Se utiliza como una dependencia en los endpoints de FastAPI para restringir el acceso según el rol del usuario. Por ejemplo:    
    @router.get("/admin-only", dependencies=[Depends(require_role(PerfilUsuario.admin))])        def admin_only_endpoint():            return {"message": "Solo los administradores pueden ver esto"}
    """
    def role_checker(user=Depends(get_current_user)):
        if user["perfil"] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos suficientes")
        return user
    return role_checker