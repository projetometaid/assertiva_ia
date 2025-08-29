"""
Utilitários para senhas
"""
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """Gera hash da senha usando Werkzeug"""
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """Verifica senha usando Werkzeug"""
    return check_password_hash(password_hash, password)
