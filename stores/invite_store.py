"""
Armazenamento e acesso a dados de convites
"""
import json
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from config.settings import INVITES_FILE, ensure_data_dir, JWT_SECRET, INVITE_TTL_MINUTES


def load_invites() -> List[Dict]:
    """Carrega convites do arquivo JSON"""
    ensure_data_dir()
    try:
        with open(INVITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_invites(invites_data: List[Dict]) -> None:
    """Salva convites no arquivo JSON"""
    ensure_data_dir()
    with open(INVITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(invites_data, f, indent=2, ensure_ascii=False)


def generate_invite_token(email: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera token de convite
    
    Returns:
        Tuple[token, error_message]
    """
    try:
        # Verificar se já existe convite ativo para este email
        if has_active_invite(email):
            return None, "Já existe um convite ativo para este email"
        
        # Gerar token
        token_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(minutes=INVITE_TTL_MINUTES)
        
        payload = {
            'email': email,
            'jti': token_id,
            'iat': int(now.timestamp()),
            'exp': int(exp_time.timestamp())
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        # Salvar convite
        invites = load_invites()
        invite_data = {
            'token_id': token_id,
            'email': email,
            'created_at': now.isoformat(),
            'expires_at': exp_time.isoformat(),
            'used': False,
            'used_at': None
        }
        invites.append(invite_data)
        save_invites(invites)
        
        return token, None
        
    except Exception as e:
        return None, f"Erro ao gerar convite: {str(e)}"


def validate_invite_token(token: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida token de convite
    
    Returns:
        Tuple[is_valid, email, error_message]
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        email = payload.get('email')
        token_id = payload.get('jti')
        
        if not email or not token_id:
            return False, None, "Token inválido"
        
        # Verificar se convite existe e não foi usado
        invites = load_invites()
        for invite in invites:
            if invite['token_id'] == token_id:
                if invite['used']:
                    return False, None, "Convite já foi usado"
                return True, email, None
        
        return False, None, "Convite não encontrado"
        
    except jwt.ExpiredSignatureError:
        return False, None, "Convite expirado"
    except jwt.InvalidTokenError:
        return False, None, "Token inválido"


def use_invite_token(token: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Marca convite como usado
    
    Returns:
        Tuple[success, email, error_message]
    """
    try:
        # Validar token primeiro
        valid, email, error = validate_invite_token(token)
        if not valid:
            return False, None, error
        
        # Marcar como usado
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        token_id = payload.get('jti')
        
        invites = load_invites()
        for invite in invites:
            if invite['token_id'] == token_id:
                invite['used'] = True
                invite['used_at'] = datetime.now(timezone.utc).isoformat()
                break
        
        save_invites(invites)
        return True, email, None
        
    except Exception as e:
        return False, None, f"Erro ao usar convite: {str(e)}"


def has_active_invite(email: str) -> bool:
    """Verifica se existe convite ativo para o email"""
    invites = load_invites()
    now = datetime.now(timezone.utc)

    for invite in invites:
        if (invite.get('email', '').lower() == email.lower() and
            not invite.get('used', False)):
            try:
                # Verificar se não expirou
                expires_at_str = invite.get('expires_at', '')
                if isinstance(expires_at_str, str):
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                else:
                    expires_at = datetime.fromtimestamp(expires_at_str, tz=timezone.utc)

                if expires_at > now:
                    return True
            except (ValueError, TypeError, KeyError):
                continue

    return False


def cleanup_expired_invites() -> int:
    """Remove convites expirados e retorna quantidade removida"""
    invites = load_invites()
    now = datetime.now(timezone.utc)

    original_count = len(invites)
    active_invites = []

    for invite in invites:
        try:
            expires_at_str = invite.get('expires_at', '')
            if isinstance(expires_at_str, str):
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            else:
                # Se não for string, assumir que é timestamp
                expires_at = datetime.fromtimestamp(expires_at_str, tz=timezone.utc)

            if expires_at > now or invite.get('used', False):
                active_invites.append(invite)
        except (ValueError, TypeError, KeyError):
            # Se houver erro na data, remover o convite
            print(f"⚠️ Removendo convite com data inválida: {invite}")
            continue

    save_invites(active_invites)
    removed_count = original_count - len(active_invites)

    if removed_count > 0:
        print(f"🧹 Removidos {removed_count} convites expirados")

    return removed_count
