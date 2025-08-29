"""
Rotas API (JSON)
"""
from flask import Blueprint, request, jsonify, make_response, redirect, url_for

from security.auth import require_auth, require_role, get_current_user
from security.cookies import set_cookie, clear_auth_cookies
from services.auth_service import authenticate_user, generate_user_tokens
from services.user_service import (
    create_invite, accept_invite, change_user_role, 
    delete_user_safe, get_users_paginated
)
from config.settings import JWT_ACCESS_TTL_MIN, JWT_REFRESH_TTL_DAYS

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/login', methods=['POST'])
def login():
    """API de login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
        
        # Autenticar usuário
        success, user, error = authenticate_user(email, password)
        if not success:
            return jsonify({'erro': error}), 401
        
        # Gerar tokens
        access_token, refresh_token = generate_user_tokens(user['id'])
        
        # Configurar cookies
        response = make_response(jsonify({
            'sucesso': True,
            'usuario': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
        }))
        
        set_cookie(response, 'access_token', access_token, JWT_ACCESS_TTL_MIN * 60)
        set_cookie(response, 'refresh_token', refresh_token, JWT_REFRESH_TTL_DAYS * 24 * 60 * 60)
        
        print(f"✅ Login realizado: {email}")
        return response
        
    except Exception as e:
        print(f"❌ Erro no login: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/logout', methods=['POST'])
def logout():
    """API de logout"""
    try:
        response = make_response(redirect(url_for('web.login')))
        clear_auth_cookies(response)
        print("✅ Logout realizado")
        return response
        
    except Exception as e:
        print(f"❌ Erro no logout: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/gerar-convite', methods=['POST'])
@require_role('admin')
def gerar_convite():
    """API para gerar convite"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'erro': 'Email é obrigatório'}), 400
        
        # Criar convite
        success, token, error = create_invite(email)
        if not success:
            return jsonify({'erro': error}), 400
        
        # Gerar URL do convite
        base_url = request.url_root.rstrip('/')
        invite_url = f"{base_url}/convite?token={token}"
        
        print(f"✅ Convite gerado para: {email}")
        
        return jsonify({
            'sucesso': True,
            'url': invite_url,
            'email': email
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar convite: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/aceitar-convite', methods=['POST'])
def aceitar_convite():
    """API para aceitar convite"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not token or not password:
            return jsonify({'erro': 'Token e senha são obrigatórios'}), 400
        
        # Aceitar convite
        success, error = accept_invite(token, password, name or None)
        if not success:
            return jsonify({'erro': error}), 400
        
        print("✅ Convite aceito e usuário criado")
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Usuário criado com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao aceitar convite: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/users', methods=['GET'])
@require_role('admin')
def list_users():
    """API para listar usuários"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        users = get_users_paginated(limit, offset)
        
        return jsonify({
            'sucesso': True,
            'usuarios': users,
            'total': len(users)
        })
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/users/<user_id>', methods=['PATCH'])
@require_role('admin')
def update_user(user_id):
    """API para atualizar usuário"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'erro': 'Role é obrigatória'}), 400
        
        # Alterar role
        success, error = change_user_role(current_user['id'], user_id, new_role)
        if not success:
            return jsonify({'erro': error}), 400
        
        print(f"✅ Role alterada para {new_role}: {user_id}")
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Role atualizada com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao atualizar usuário: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@api.route('/users/<user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    """API para excluir usuário"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        confirmation = data.get('confirmation', '')
        
        # Excluir usuário
        success, error = delete_user_safe(current_user['id'], user_id, confirmation)
        if not success:
            return jsonify({'erro': error}), 400
        
        print(f"✅ Usuário excluído: {user_id}")
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Usuário excluído com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao excluir usuário: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
