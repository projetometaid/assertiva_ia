from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import wraps
import uuid
import json
import hashlib
import jwt
import secrets

# Adicionar o diretório pai ao path para importar o sistema de apoio
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sistema_apoio_atendimento import SistemaApoioAtendimento
except ImportError:
    print("⚠️  Sistema de apoio não encontrado. Usando modo demo.")
    SistemaApoioAtendimento = None

print("🔧 Carregando sistema de autenticação com JWT...")

# Configurações JWT
JWT_SECRET = os.environ.get('JWT_SESSION_SECRET', 'dev-secret-session-change-in-production')
JWT_ACCESS_TTL_MIN = int(os.environ.get('JWT_ACCESS_TTL_MIN', '15'))
JWT_REFRESH_TTL_DAYS = int(os.environ.get('JWT_REFRESH_TTL_DAYS', '7'))

# Usuário admin inicial (seed)
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@assertiva.local')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Sistema de usuários
USERS_FILE = 'data/users.json'
SYSTEM_USER_ID = 'system-user-00000000-0000-0000-0000-000000000000'

def _hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_data_dir():
    """Garante que o diretório data existe"""
    os.makedirs('data', exist_ok=True)

def load_users():
    """Carrega usuários do arquivo JSON"""
    ensure_data_dir()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users_data):
    """Salva usuários no arquivo JSON"""
    ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)

def create_admin_seed():
    """Cria usuário admin inicial se não existir"""
    users = load_users()

    # Criar usuário SYSTEM se não existir
    if SYSTEM_USER_ID not in users:
        users[SYSTEM_USER_ID] = {
            'id': SYSTEM_USER_ID,
            'email': 'system@assertiva.internal',
            'role': 'system',
            'passwordHash': None,
            'name': 'Sistema',
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat(),
            'deletedAt': None
        }

    # Criar admin se não existir
    admin_exists = any(
        user.get('email') == ADMIN_EMAIL and user.get('deletedAt') is None
        for user in users.values()
    )

    if not admin_exists:
        admin_id = str(uuid.uuid4())
        users[admin_id] = {
            'id': admin_id,
            'email': ADMIN_EMAIL,
            'role': 'admin',
            'passwordHash': _hash_password(ADMIN_PASSWORD),
            'name': 'Administrador',
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat(),
            'deletedAt': None
        }
        save_users(users)
        print(f"✅ Admin criado: {ADMIN_EMAIL}")

# Funções JWT
def generate_tokens(user_id, email, role):
    """Gera access e refresh tokens"""
    now = datetime.now(timezone.utc)

    # Access token (curto)
    access_payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(minutes=JWT_ACCESS_TTL_MIN)
    }

    # Refresh token (longo)
    refresh_payload = {
        'user_id': user_id,
        'email': email,
        'type': 'refresh',
        'iat': now,
        'exp': now + timedelta(days=JWT_REFRESH_TTL_DAYS)
    }

    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm='HS256')

    return access_token, refresh_token

def verify_token(token, token_type='access'):
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None, 'Tipo de token inválido'
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expirado'
    except jwt.InvalidTokenError:
        return None, 'Token inválido'

def get_current_user():
    """Obtém usuário atual da sessão"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        return None

    payload, error = verify_token(access_token, 'access')
    if error:
        return None

    users = load_users()
    user_data = users.get(payload['user_id'])
    if not user_data or user_data.get('deletedAt'):
        return None

    return {
        'id': user_data['id'],
        'email': user_data['email'],
        'role': user_data['role'],
        'name': user_data.get('name', '')
    }

def require_auth(f):
    """Decorator que exige autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json:
                return jsonify({'erro': 'Token de acesso inválido ou expirado'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """Decorator que exige role específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json:
                    return jsonify({'erro': 'Token de acesso inválido ou expirado'}), 401
                return redirect(url_for('login'))

            if user['role'] != required_role:
                if request.is_json:
                    return jsonify({'erro': 'Permissão insuficiente'}), 403
                flash('Você não tem permissão para acessar esta página.', 'error')
                return redirect(url_for('atendimento'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Inicializar sistema
create_admin_seed()
USERS_DB = load_users()

# Sistema de convites
INVITES_FILE = 'data/invites.json'
INVITE_TTL_MINUTES = 30

def load_invites():
    """Carrega convites do arquivo JSON"""
    ensure_data_dir()
    try:
        if os.path.exists(INVITES_FILE):
            with open(INVITES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_invites(invites):
    """Salva convites no arquivo JSON"""
    ensure_data_dir()
    with open(INVITES_FILE, 'w') as f:
        json.dump(invites, f, indent=2)

def clean_expired_invites():
    """Remove convites expirados"""
    invites = load_invites()
    now = datetime.now().timestamp()
    valid_invites = [inv for inv in invites if inv['expires_at'] > now and not inv['used']]
    if len(valid_invites) != len(invites):
        save_invites(valid_invites)
    return valid_invites

def generate_invite(email):
    """Gera um convite para o email especificado"""
    clean_expired_invites()

    # Verificar se já existe convite válido para este email
    invites = load_invites()
    for invite in invites:
        if invite['email'] == email and not invite['used']:
            return None, "Já existe um convite válido para este email"

    # Gerar token
    token_id = secrets.token_urlsafe(16)
    expires_at = datetime.now() + timedelta(minutes=INVITE_TTL_MINUTES)

    token_data = {
        'sub': email,
        'jti': token_id,
        'typ': 'invite',
        'exp': expires_at.timestamp()
    }

    token = jwt.encode(token_data, JWT_SECRET, algorithm='HS256')

    # Salvar convite
    invite_data = {
        'token_id': token_id,
        'email': email,
        'expires_at': expires_at.timestamp(),
        'used': False,
        'created_at': datetime.now().isoformat()
    }

    invites.append(invite_data)
    save_invites(invites)

    return token, None

def validate_invite_token(token):
    """Valida token de convite"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        token_id = payload.get('jti')
        email = payload.get('sub')

        # Verificar se convite existe e é válido
        invites = load_invites()
        for invite in invites:
            if (invite['token_id'] == token_id and
                invite['email'] == email and
                not invite['used'] and
                invite['expires_at'] > datetime.now().timestamp()):
                return True, email, None

        return False, None, "Convite inválido, usado ou expirado"

    except jwt.ExpiredSignatureError:
        return False, None, "Convite expirado"
    except jwt.InvalidTokenError:
        return False, None, "Token inválido"

def use_invite_token(token, password):
    """Usa o token de convite para criar usuário"""
    valid, email, error = validate_invite_token(token)
    if not valid:
        return False, error

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        token_id = payload.get('jti')

        # Marcar convite como usado
        invites = load_invites()
        for invite in invites:
            if invite['token_id'] == token_id:
                invite['used'] = True
                invite['used_at'] = datetime.now().isoformat()
                break
        save_invites(invites)

        # Adicionar usuário ao sistema
        users = load_users()
        user_id = str(uuid.uuid4())

        users[user_id] = {
            'id': user_id,
            'email': email,
            'role': 'atendente',  # Role padrão
            'passwordHash': _hash_password(password),
            'name': email.split('@')[0].title(),
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat(),
            'deletedAt': None
        }

        save_users(users)
        print(f"✅ Usuário criado: {email} (role: atendente)")

        return True, "Usuário criado com sucesso"

    except Exception as e:
        return False, f"Erro ao criar usuário: {str(e)}"



def login_required(f):
    """Decorator para rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para rotas que requerem privilégios de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))

        user = session.get('user')
        if user.get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna dados do usuário atual da sessão"""
    return session.get('user')

def is_admin():
    """Verifica se o usuário atual é admin"""
    user = get_current_user()
    return user and user.get('role') == 'admin'

# Sistema de autenticação sempre disponível
auth_system = True
print("✅ Sistema de autenticação DIRETO carregado com sucesso!")

# Middleware de segurança
def no_cache(f):
    """Decorator para bloquear cache em páginas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Surrogate-Control'] = 'no-store'
        return response
    return decorated_function

def check_session_expiry():
    """Verifica se a sessão expirou e renova se ativa"""
    if 'user' in session:
        # Marcar sessão como permanente para usar o timeout configurado
        session.permanent = True

        # Verificar última atividade
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity > FOUR_HOURS:
                session.clear()
                return False

        # Atualizar última atividade
        session['last_activity'] = datetime.now().isoformat()
        return True
    return False

def require_auth_with_security(f):
    """Decorator combinado: autenticação + no-cache + verificação de sessão"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar expiração da sessão
        if not check_session_expiry():
            flash('Sua sessão expirou. Faça login novamente.', 'warning')
            return redirect(url_for('login'))

        # Verificar autenticação
        if 'user' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))

        # Aplicar no-cache
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Surrogate-Control'] = 'no-store'
        return response
    return decorated_function

def require_admin_with_security(f):
    """Decorator para rotas que requerem admin + segurança"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar expiração da sessão
        if not check_session_expiry():
            flash('Sua sessão expirou. Faça login novamente.', 'warning')
            return redirect(url_for('login'))

        # Verificar autenticação
        if 'user' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))

        # Verificar privilégios de admin
        user = session.get('user')
        if user.get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('atendimento'))

        # Aplicar no-cache
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Surrogate-Control'] = 'no-store'
        return response
    return decorated_function

app = Flask(__name__)

# Configurar Lucide Icons
# lucide.init_app(app)  # Comentado temporariamente para resolver erro de importação

# Configuração de segurança da sessão
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Sessão expira em 4 horas
FOUR_HOURS = timedelta(hours=4)
app.permanent_session_lifetime = FOUR_HOURS

# Configurações de cookie seguro
is_production = os.environ.get('FLASK_ENV') == 'production'
has_https = True  # HTTPS agora está configurado
app.config.update(
    SESSION_COOKIE_SECURE=has_https,  # HTTPS está disponível
    SESSION_COOKIE_HTTPONLY=True,  # Não acessível via JavaScript
    SESSION_COOKIE_SAMESITE='Lax',  # Proteção CSRF
    SESSION_COOKIE_NAME='assertiva_session'
)

# Inicializar sistema de apoio
try:
    sistema_apoio = SistemaApoioAtendimento() if SistemaApoioAtendimento else None
except Exception as e:
    print(f"⚠️  Erro ao inicializar sistema: {e}")
    sistema_apoio = None

# ===== ROTAS DE AUTENTICAÇÃO =====

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """API de login com JWT"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

        # Buscar usuário
        users = load_users()
        user = None
        for user_data in users.values():
            if (user_data.get('email', '').lower() == email and
                user_data.get('deletedAt') is None):
                user = user_data
                break

        if not user or user.get('passwordHash') != _hash_password(password):
            return jsonify({'erro': 'Email ou senha inválidos'}), 401

        # Gerar tokens
        access_token, refresh_token = generate_tokens(
            user['id'], user['email'], user['role']
        )

        # Criar response com cookies httpOnly
        response = make_response(jsonify({
            'sucesso': True,
            'user': {
                'email': user['email'],
                'role': user['role'],
                'name': user.get('name', '')
            }
        }))

        # Configurar cookies httpOnly
        response.set_cookie(
            'access_token', access_token,
            max_age=JWT_ACCESS_TTL_MIN * 60,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        response.set_cookie(
            'refresh_token', refresh_token,
            max_age=JWT_REFRESH_TTL_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        print(f"✅ Login JWT realizado: {user['email']}")
        return response

    except Exception as e:
        print(f"❌ Erro no login: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    """Renovar access token usando refresh token"""
    try:
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            return jsonify({'erro': 'Refresh token não encontrado'}), 401

        payload, error = verify_token(refresh_token, 'refresh')
        if error:
            return jsonify({'erro': error}), 401

        # Verificar se usuário ainda existe e está ativo
        users = load_users()
        user = users.get(payload['user_id'])
        if not user or user.get('deletedAt'):
            return jsonify({'erro': 'Usuário não encontrado ou inativo'}), 401

        # Gerar novo access token
        access_token, _ = generate_tokens(
            user['id'], user['email'], user['role']
        )

        response = make_response(jsonify({'sucesso': True}))
        response.set_cookie(
            'access_token', access_token,
            max_age=JWT_ACCESS_TTL_MIN * 60,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response

    except Exception as e:
        print(f"❌ Erro no refresh: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Logout - limpar cookies"""
    response = make_response(jsonify({'sucesso': True}))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    print("🚪 Logout JWT realizado")
    return response

@app.route('/me')
@require_auth
def get_me():
    """Retorna dados do usuário autenticado"""
    user = get_current_user()
    return jsonify({
        'email': user['email'],
        'role': user['role'],
        'name': user['name']
    })

@app.route('/')
def index():
    """Página inicial - redireciona para login se não autenticado, depois para atendimento"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return redirect(url_for('atendimento'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Se já está logado, redirecionar
    user = get_current_user()
    if user:
        return redirect(url_for('atendimento'))

    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout - redireciona para página de login"""
    response = make_response(redirect(url_for('login')))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)

    # Headers de no-cache
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    flash('Logout realizado com sucesso', 'success')
    return response

@app.route('/atendimento')
@require_auth
def atendimento():
    """Página principal do sistema de atendimento"""
    return render_template('atendimento.html', user=get_current_user())


@app.route('/api/responder', methods=['POST'])
@require_auth
def api_responder():
    """API para gerar respostas de atendimento com segurança"""
    print("🔄 [LOG] Iniciando processamento da pergunta...")

    try:
        data = request.get_json()
        print(f"📥 [LOG] Dados recebidos: {data}")

        pergunta = data.get('pergunta', '').strip()
        print(f"❓ [LOG] Pergunta extraída: '{pergunta}'")

        if not pergunta:
            print("❌ [LOG] Pergunta vazia!")
            return jsonify({'erro': 'Pergunta não pode estar vazia'}), 400

        print(f"🤖 [LOG] Status do sistema_apoio: {sistema_apoio is not None}")

        if not sistema_apoio:
            print("⚠️ [LOG] Sistema em modo demo - sem OpenAI")
            return jsonify({
                'resposta': 'Sistema em modo demo. Configure a API OpenAI para funcionalidade completa.'
            })

        print("🚀 [LOG] Chamando sistema_apoio.gerar_resposta_atendimento...")

        # Gerar resposta
        resposta = sistema_apoio.gerar_resposta_atendimento(pergunta)
        print(f"✅ [LOG] Resposta gerada com sucesso: {len(resposta)} caracteres")

        # Salvar na sessão (temporário)
        if 'historico' not in session:
            session['historico'] = []

        session['historico'].append({
            'pergunta': pergunta,
            'resposta': resposta
        })

        print("💾 [LOG] Resposta salva no histórico")
        return jsonify({'resposta': resposta})

    except Exception as e:
        print(f"💥 [LOG] ERRO: {str(e)}")
        import traceback
        print(f"📋 [LOG] Traceback: {traceback.format_exc()}")
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@app.route('/api/historico')
def api_historico():
    """API para obter histórico de perguntas"""
    return jsonify(session.get('historico', []))

@app.route('/admin')
@require_role('admin')
def admin():
    """Painel administrativo"""
    return render_template('admin.html', user=get_current_user())

@app.route('/configuracoes')
@require_role('admin')
def configuracoes():
    """Página de configurações do sistema"""
    return render_template('configuracoes.html', user=get_current_user())

# ===== ROTAS DE GESTÃO DE USUÁRIOS =====

@app.route('/users')
@require_role('admin')
def list_users():
    """Lista usuários ativos"""
    try:
        users = load_users()
        active_users = []

        for user_data in users.values():
            if user_data.get('deletedAt') is None and user_data.get('role') != 'system':
                active_users.append({
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'name': user_data.get('name', ''),
                    'createdAt': user_data.get('createdAt', '')
                })

        # Ordenar por email
        active_users.sort(key=lambda x: x['email'])

        return jsonify({
            'users': active_users,
            'total': len(active_users)
        })

    except Exception as e:
        print(f"❌ Erro ao listar usuários: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/users/<user_id>', methods=['PATCH'])
@require_role('admin')
def update_user(user_id):
    """Atualizar role do usuário"""
    try:
        data = request.get_json()
        new_role = data.get('role')

        if new_role not in ['admin', 'atendente']:
            return jsonify({'erro': 'Role inválida'}), 400

        users = load_users()
        if user_id not in users:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        user = users[user_id]
        if user.get('deletedAt'):
            return jsonify({'erro': 'Usuário foi removido'}), 404

        # Atualizar role
        user['role'] = new_role
        user['updatedAt'] = datetime.now(timezone.utc).isoformat()

        save_users(users)

        print(f"✅ Role atualizada: {user['email']} -> {new_role}")

        return jsonify({
            'sucesso': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'name': user.get('name', '')
            }
        })

    except Exception as e:
        print(f"❌ Erro ao atualizar usuário: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

def reassign_or_anonymize(user_id):
    """Reatribui ou anonimiza dados do usuário removido"""
    try:
        # Aqui você implementaria a lógica para reatribuir dados
        # Por exemplo: histórico de atendimentos, logs, etc.
        # Para este exemplo, apenas logamos a ação
        print(f"🔄 Reatribuindo dados do usuário {user_id} para SYSTEM_USER")

        # Implementar conforme necessário:
        # - Transferir ownership de registros para SYSTEM_USER_ID
        # - Anonimizar campos pessoais
        # - Atualizar referências em outras tabelas

        return True
    except Exception as e:
        print(f"❌ Erro ao reatribuir dados: {str(e)}")
        return False

@app.route('/users/<user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    """Exclusão segura de usuário"""
    try:
        data = request.get_json()
        confirmation = data.get('confirmation', '')

        users = load_users()
        if user_id not in users:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        user = users[user_id]
        if user.get('deletedAt'):
            return jsonify({'erro': 'Usuário já foi removido'}), 404

        # Verificar confirmação (email do usuário)
        if confirmation.lower() != user['email'].lower():
            return jsonify({'erro': 'Confirmação inválida'}), 400

        # Não permitir auto-exclusão
        current_user = get_current_user()
        if current_user['id'] == user_id:
            return jsonify({'erro': 'Não é possível excluir sua própria conta'}), 400

        # Reatribuir dados
        if not reassign_or_anonymize(user_id):
            return jsonify({'erro': 'Erro ao reatribuir dados do usuário'}), 500

        # Soft delete
        user['deletedAt'] = datetime.now(timezone.utc).isoformat()
        user['updatedAt'] = datetime.now(timezone.utc).isoformat()

        save_users(users)

        print(f"🗑️ Usuário removido: {user['email']}")

        return jsonify({'sucesso': True})

    except Exception as e:
        print(f"❌ Erro ao remover usuário: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/gerar-convite', methods=['POST'])
@require_role('admin')
def api_gerar_convite():
    """API para gerar convite de usuário"""
    try:
        print(f"🔍 [CONVITE] Recebendo requisição...")
        data = request.get_json()
        print(f"🔍 [CONVITE] Dados recebidos: {data}")

        email = data.get('email', '').strip().lower()
        print(f"🔍 [CONVITE] Email processado: '{email}'")

        if not email:
            print(f"❌ [CONVITE] Email vazio")
            return jsonify({'erro': 'Email é obrigatório'}), 400

        # Validar formato do email
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            print(f"❌ [CONVITE] Formato de email inválido: {email}")
            return jsonify({'erro': 'Formato de email inválido'}), 400

        # Verificar se usuário já existe
        print(f"🔍 [CONVITE] Verificando se usuário já existe...")
        users = load_users()
        user_exists = any(
            user_data.get('email', '').lower() == email and user_data.get('deletedAt') is None
            for user_data in users.values()
        )

        if user_exists:
            print(f"❌ [CONVITE] Usuário já existe: {email}")
            return jsonify({'erro': 'Usuário já cadastrado'}), 400

        print(f"🔍 [CONVITE] Usuário não existe, gerando convite...")
        # Gerar convite
        token, error = generate_invite(email)
        print(f"🔍 [CONVITE] Resultado generate_invite: token={token}, error={error}")
        if error:
            print(f"❌ [CONVITE] Erro ao gerar convite: {error}")
            return jsonify({'erro': error}), 400

        # Gerar URL do convite
        base_url = request.url_root.rstrip('/')
        invite_url = f"{base_url}/convite?token={token}"

        print(f"✅ Convite gerado para: {email}")

        return jsonify({
            'sucesso': True,
            'url': invite_url,
            'email': email,
            'expira_em': f"{INVITE_TTL_MINUTES} minutos"
        })

    except Exception as e:
        print(f"❌ Erro ao gerar convite: {str(e)}")
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@app.route('/convite')
def convite():
    """Página para aceitar convite"""
    token = request.args.get('token')
    if not token:
        flash('Token de convite não encontrado', 'error')
        return redirect(url_for('login'))

    # Validar token
    valid, email, error = validate_invite_token(token)
    if not valid:
        flash(f'Convite inválido: {error}', 'error')
        return redirect(url_for('login'))

    return render_template('convite.html', token=token, email=email)

@app.route('/api/aceitar-convite', methods=['POST'])
def api_aceitar_convite():
    """API para aceitar convite e definir senha"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        password = data.get('password', '')

        if not token or not password:
            return jsonify({'erro': 'Token e senha são obrigatórios'}), 400

        if len(password) < 8:
            return jsonify({'erro': 'Senha deve ter pelo menos 8 caracteres'}), 400

        # Usar convite
        success, message = use_invite_token(token, password)
        if not success:
            return jsonify({'erro': message}), 400

        print(f"✅ Convite aceito e usuário criado")

        return jsonify({
            'sucesso': True,
            'mensagem': message
        })

    except Exception as e:
        print(f"❌ Erro ao aceitar convite: {str(e)}")
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check para AWS"""
    return jsonify({
        'status': 'healthy',
        'sistema_apoio': sistema_apoio is not None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
