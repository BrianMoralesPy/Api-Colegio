import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")

def password_ya_usada(password: str, hashes: list[str]) -> bool:
    for h in hashes:
        if bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8")):
            return True
    return False