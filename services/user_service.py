"""
Serviços de gestão de usuários
"""
import re
from typing import Optional, Tuple, Dict, List

from stores.user_store import (
    create_user, get_user_by_email, update_user_role, 
    soft_delete_user, list_users, reassign_or_anonymize,
    user_exists_by_email
)
from stores.invite_store import generate_invite_token, use_invite_token
from services.auth_service import can_modify_user, can_change_role
from config.settings import SYSTEM_USER_ID


def validate_email(email: str) -> bool:
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_invite(email: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Cria convite para novo usuário
    
    Returns:
        Tuple[success, invite_token, error_message]
    """
    try:
        # Validar email
        if not validate_email(email):
            return False, None, "Email inválido"
        
        # Verificar se usuário já existe
        if user_exists_by_email(email):
            return False, None, "Usuário já cadastrado"
        
        # Gerar convite
        token, error = generate_invite_token(email)
        if error:
            return False, None, error
        
        return True, token, None
        
    except Exception as e:
        return False, None, f"Erro interno: {str(e)}"


def accept_invite(token: str, password: str, name: str = None) -> Tuple[bool, Optional[str]]:
    """
    Aceita convite e cria usuário
    
    Returns:
        Tuple[success, error_message]
    """
    try:
        # Validar senha
        if len(password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"
        
        # Usar token de convite
        success, email, error = use_invite_token(token)
        if not success:
            return False, error
        
        # Criar usuário
        user_id = create_user(email, password, 'atendente', name)
        print(f"✅ Usuário criado: {email} (ID: {user_id})")
        
        return True, None
        
    except Exception as e:
        return False, f"Erro interno: {str(e)}"


def change_user_role(current_user_id: str, target_user_id: str, new_role: str) -> Tuple[bool, Optional[str]]:
    """
    Altera role de usuário

    Returns:
        Tuple[success, error_message]
    """
    try:
        # Verificar se é o usuário protegido
        from stores.user_store import get_user_by_id
        target_user = get_user_by_id(target_user_id)
        if target_user and target_user.get('email') == 'leandro.albertini@assertivasolucoes.com.br':
            return False, "Este usuário está protegido e não pode ter o perfil alterado"

        # Verificar permissões
        can_change, error = can_change_role(current_user_id, target_user_id, new_role)
        if not can_change:
            return False, error
        
        # Atualizar role
        success = update_user_role(target_user_id, new_role)
        if not success:
            return False, "Usuário não encontrado"
        
        return True, None
        
    except Exception as e:
        return False, f"Erro interno: {str(e)}"


def delete_user_safe(current_user_id: str, target_user_id: str, confirmation: str) -> Tuple[bool, Optional[str]]:
    """
    Exclui usuário com segurança

    Returns:
        Tuple[success, error_message]
    """
    try:
        # Verificar se é o usuário protegido
        from stores.user_store import get_user_by_id
        target_user = get_user_by_id(target_user_id)
        if target_user and target_user.get('email') == 'leandro.albertini@assertivasolucoes.com.br':
            return False, "Este usuário está protegido e não pode ser excluído"

        # Verificar permissões
        can_modify, error = can_modify_user(current_user_id, target_user_id)
        if not can_modify:
            return False, error

        # Verificar confirmação (agora aceita o email como confirmação)
        if target_user and confirmation != target_user.get('email'):
            return False, "Email de confirmação não confere"
        
        # Reatribuir dados antes da exclusão
        if not reassign_or_anonymize(target_user_id, SYSTEM_USER_ID):
            return False, "Erro ao reatribuir dados do usuário"
        
        # Soft delete
        success = soft_delete_user(target_user_id)
        if not success:
            return False, "Usuário não encontrado"
        
        return True, None
        
    except Exception as e:
        return False, f"Erro interno: {str(e)}"


def get_users_paginated(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Obtém lista paginada de usuários"""
    # Validar parâmetros
    limit = max(1, min(limit, 100))  # Entre 1 e 100
    offset = max(0, offset)
    
    return list_users(limit, offset)
