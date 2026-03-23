# core/security/hashing.py
import bcrypt

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt y devuelve el hash resultante como una cadena de texto.
    Args:
        password (str): La contraseña en texto plano que se desea hashear.
    Returns:
        str: El hash de la contraseña generado por bcrypt, decodificado a UTF-8
    """
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")

def password_ya_usada(password: str, hashes: list[str]) -> bool:
    """
    Verifica si una contraseña en texto plano ya ha sido usada comparándola con una lista de hashes de contraseñas anteriores.
    Args:
        password (str): La contraseña en texto plano que se desea verificar.
        hashes (list[str]): Una lista de hashes de contraseñas anteriores contra los cuales se comparará la contraseña proporcionada.   
    Returns:
        bool: True si la contraseña ya ha sido usada (es decir, si coincide con alguno de los hashes proporcionados), False en caso contrario.
    """
    for h in hashes:
        if bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8")):
            return True
    return False