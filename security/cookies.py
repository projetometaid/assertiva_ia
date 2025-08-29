"""
Gerenciamento de cookies seguros
"""
from config.settings import IS_PRODUCTION


def set_cookie(response, name, value, max_age, secure=None):
    """
    Define cookie com configurações condicionais de segurança
    
    Args:
        response: Flask response object
        name: Nome do cookie
        value: Valor do cookie
        max_age: Tempo de vida em segundos
        secure: Se None, usa IS_PRODUCTION
    """
    if secure is None:
        secure = IS_PRODUCTION
    
    response.set_cookie(
        name, 
        value, 
        max_age=max_age, 
        httponly=True, 
        secure=secure, 
        samesite='Lax'
    )


def clear_auth_cookies(response):
    """Remove cookies de autenticação"""
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
