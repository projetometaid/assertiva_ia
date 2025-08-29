"""
Configurações centralizadas do sistema
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
INVITES_FILE = DATA_DIR / "invites.json"

# Configurações de ambiente
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
IS_PRODUCTION = FLASK_ENV == 'production'

# JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
JWT_ACCESS_TTL_MIN = int(os.environ.get('JWT_ACCESS_TTL_MIN', '15'))
JWT_REFRESH_TTL_DAYS = int(os.environ.get('JWT_REFRESH_TTL_DAYS', '7'))

# Convites
INVITE_TTL_MINUTES = int(os.environ.get('INVITE_TTL_MINUTES', '30'))

# Admin padrão
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@assertiva.local')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Sistema
SYSTEM_USER_ID = 'system-user-00000000-0000-0000-0000-000000000000'

# CORS
VITE_ORIGIN = os.environ.get('VITE_ORIGIN', 'http://localhost:3000')

# OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

def ensure_data_dir():
    """Garante que o diretório data existe"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
