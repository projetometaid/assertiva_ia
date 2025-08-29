"""
Serviços de autenticação e autorização
"""
from typing import Optional, Tuple, Dict

from security.auth import generate_tokens
from security.password import verify_password
from stores.user_store import get_user_by_email
from config.settings import SYSTEM_USER_ID


def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Autentica usuário com email e senha
    
    Returns:
        Tuple[success, user_data, error_message]
    """
    try:
        user = get_user_by_email(email)
        if not user:
            return False, None, "Email ou senha inválidos"
        
        if not verify_password(user.get('passwordHash', ''), password):
            return False, None, "Email ou senha inválidos"
        
        return True, user, None
        
    except Exception as e:
        return False, None, f"Erro interno: {str(e)}"


def generate_user_tokens(user_id: str) -> Tuple[str, str]:
    """Gera tokens JWT para o usuário"""
    return generate_tokens(user_id)


def can_modify_user(current_user_id: str, target_user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica se usuário pode modificar outro usuário
    
    Returns:
        Tuple[can_modify, error_message]
    """
    # Não pode modificar usuário do sistema
    if target_user_id == SYSTEM_USER_ID:
        return False, "Operação não permitida"
    
    # Não pode se auto-excluir
    if current_user_id == target_user_id:
        return False, "Não é possível modificar seu próprio usuário"
    
    return True, None


def can_change_role(current_user_id: str, target_user_id: str, new_role: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica se usuário pode alterar role de outro usuário
    
    Returns:
        Tuple[can_change, error_message]
    """
    # Verificações básicas
    can_modify, error = can_modify_user(current_user_id, target_user_id)
    if not can_modify:
        return False, error
    
    # Não pode alterar próprio role
    if current_user_id == target_user_id:
        return False, "Não é possível alterar seu próprio role"
    
    # Validar role
    if new_role not in ['admin', 'atendente']:
        return False, "Role inválida"
    
    return True, None
