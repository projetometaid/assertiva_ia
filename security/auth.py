"""
Sistema de autenticação JWT
"""
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, redirect, url_for, flash

from config.settings import JWT_SECRET, JWT_ACCESS_TTL_MIN, JWT_REFRESH_TTL_DAYS


def generate_tokens(user_id):
    """Gera access e refresh tokens"""
    now = datetime.now(timezone.utc)
    
    # Access token (curto)
    access_payload = {
        'user_id': user_id,
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(minutes=JWT_ACCESS_TTL_MIN)
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
    
    # Refresh token (longo)
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': now,
        'exp': now + timedelta(days=JWT_REFRESH_TTL_DAYS)
    }
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm='HS256')
    
    return access_token, refresh_token


def verify_token(token, token_type='access'):
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """Obtém usuário atual dos cookies JWT"""
    access_token = request.cookies.get('access_token')
    print(f"🔍 [AUTH] Access token presente: {bool(access_token)}")
    if not access_token:
        print("❌ [AUTH] Nenhum access token encontrado")
        return None

    payload = verify_token(access_token, 'access')
    print(f"🔍 [AUTH] Payload válido: {bool(payload)}")
    if not payload:
        print("❌ [AUTH] Token inválido ou expirado")
        return None

    user_id = payload.get('user_id')
    print(f"🔍 [AUTH] User ID: {user_id}")
    if not user_id:
        print("❌ [AUTH] User ID não encontrado no payload")
        return None

    # Importação local para evitar circular import
    from stores.user_store import get_user_by_id
    user = get_user_by_id(user_id)
    print(f"✅ [AUTH] Usuário encontrado: {user['email'] if user else 'None'}")
    return user


def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.path.startswith('/api/'):
                return jsonify({'erro': 'Token de acesso inválido ou expirado'}), 401
            else:
                flash('Você precisa fazer login para acessar esta página.', 'warning')
                return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function


def require_role(required_role):
    """Decorator para rotas que requerem role específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.path.startswith('/api/'):
                    return jsonify({'erro': 'Token de acesso inválido ou expirado'}), 401
                else:
                    flash('Você precisa fazer login para acessar esta página.', 'warning')
                    return redirect(url_for('web.login'))
            
            if user.get('role') != required_role:
                if request.path.startswith('/api/'):
                    return jsonify({'erro': 'Permissão insuficiente'}), 403
                else:
                    flash('Você não tem permissão para acessar esta página.', 'error')
                    return redirect(url_for('web.atendimento'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator



