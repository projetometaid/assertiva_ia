"""
Armazenamento e acesso a dados de usuários
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from config.settings import USERS_FILE, ensure_data_dir, ADMIN_EMAIL, ADMIN_PASSWORD, SYSTEM_USER_ID
from security.password import hash_password


def load_users() -> Dict:
    """Carrega usuários do arquivo JSON"""
    ensure_data_dir()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_users(users_data: Dict) -> None:
    """Salva usuários no arquivo JSON"""
    ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Busca usuário por ID"""
    users = load_users()
    user = users.get(user_id)
    if user and user.get('deletedAt') is None:
        return user
    return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """Busca usuário por email"""
    users = load_users()
    for user in users.values():
        if (user.get('email', '').lower() == email.lower() and 
            user.get('deletedAt') is None):
            return user
    return None


def create_user(email: str, password: str, role: str = 'atendente', name: str = None) -> str:
    """Cria novo usuário e retorna o ID"""
    users = load_users()
    user_id = str(uuid.uuid4())
    
    if name is None:
        name = email.split('@')[0].title()
    
    users[user_id] = {
        'id': user_id,
        'email': email,
        'role': role,
        'passwordHash': hash_password(password),
        'name': name,
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat(),
        'deletedAt': None
    }
    
    save_users(users)
    return user_id


def update_user_role(user_id: str, new_role: str) -> bool:
    """Atualiza role do usuário"""
    if user_id == SYSTEM_USER_ID:
        return False
    
    users = load_users()
    if user_id not in users:
        return False
    
    users[user_id]['role'] = new_role
    users[user_id]['updatedAt'] = datetime.now(timezone.utc).isoformat()
    save_users(users)
    return True


def soft_delete_user(user_id: str) -> bool:
    """Soft delete do usuário"""
    if user_id == SYSTEM_USER_ID:
        return False
    
    users = load_users()
    if user_id not in users:
        return False
    
    users[user_id]['deletedAt'] = datetime.now(timezone.utc).isoformat()
    users[user_id]['updatedAt'] = datetime.now(timezone.utc).isoformat()
    save_users(users)
    return True


def list_users(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Lista usuários com paginação"""
    users = load_users()
    active_users = [
        user for user in users.values()
        if user.get('deletedAt') is None and user.get('role') != 'system'  # Filtrar usuário system
    ]

    # Ordenar por data de criação
    active_users.sort(key=lambda x: x.get('createdAt', ''), reverse=True)

    # Aplicar paginação
    return active_users[offset:offset + limit]


def ensure_admin_user():
    """Garante que existe um usuário admin"""
    admin_user = get_user_by_email(ADMIN_EMAIL)
    if not admin_user:
        print(f"🔧 Criando usuário admin: {ADMIN_EMAIL}")
        create_user(ADMIN_EMAIL, ADMIN_PASSWORD, 'admin', 'Administrador')
        print("✅ Usuário admin criado com sucesso!")
    else:
        # Verificar se precisa atualizar senha para Werkzeug
        if admin_user.get('passwordHash') and len(admin_user['passwordHash']) == 64:
            print(f"🔄 Atualizando senha admin para Werkzeug: {ADMIN_EMAIL}")
            users = load_users()
            users[admin_user['id']]['passwordHash'] = hash_password(ADMIN_PASSWORD)
            users[admin_user['id']]['updatedAt'] = datetime.now(timezone.utc).isoformat()
            save_users(users)
            print("✅ Senha admin atualizada para Werkzeug!")
        else:
            print(f"✅ Usuário admin já existe: {ADMIN_EMAIL}")


def reassign_or_anonymize(user_id: str, system_user_id: str) -> bool:
    """Reatribui dados do usuário para o sistema antes da exclusão"""
    try:
        # Aqui você implementaria a lógica para reatribuir
        # dados como histórico de atendimentos, etc.
        print(f"🔄 Reatribuindo dados do usuário {user_id} para {system_user_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao reatribuir dados: {str(e)}")
        return False


def user_exists_by_email(email: str) -> bool:
    """Verifica se usuário existe por email"""
    return get_user_by_email(email) is not None
