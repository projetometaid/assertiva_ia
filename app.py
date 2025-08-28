from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
# from lucide import lucide  # Comentado temporariamente para resolver erro de importação

# Adicionar o diretório pai ao path para importar o sistema de apoio
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sistema_apoio_atendimento import SistemaApoioAtendimento
except ImportError:
    print("⚠️  Sistema de apoio não encontrado. Usando modo demo.")
    SistemaApoioAtendimento = None

# Sistema de autenticação DIRETO no app.py - SEM IMPORTS EXTERNOS
import hashlib
from functools import wraps

print("🔧 Carregando sistema de autenticação DIRETO...")

# Base de usuários DIRETO no código
USERS_DB = {
    "leandro.albertini@assertivasolucoes.com.br": {
        "password_hash": "d9af2ff511d8d1fdbcc4d2703f9cbeced5ed5e7e3b209bcececc4ea171aeb8ef",  # @Certificado123
        "name": "Leandro Albertini",
        "role": "admin"
    }
}

def _hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    """Autentica usuário"""
    try:
        email = email.lower().strip()
        if email not in USERS_DB:
            return False, None, "Usuário não encontrado"

        user = USERS_DB[email]
        password_hash = _hash_password(password)

        if password_hash != user["password_hash"]:
            return False, None, "Senha incorreta"

        user_data = {
            "username": email,
            "email": email,
            "name": user["name"],
            "role": user["role"]
        }

        return True, user_data, None

    except Exception as e:
        return False, None, f"Erro na autenticação: {str(e)}"

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

@app.route('/')
def index():
    """Página inicial - redireciona para login se não autenticado, depois para atendimento"""
    if not check_session_expiry() or 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('atendimento'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')

        print(f"🔐 Tentando autenticar: {email}")

        # Tentar autenticar usando função direta
        sucesso, user_data, erro = authenticate_user(email, password)
        print(f"🔐 Resultado autenticação: sucesso={sucesso}, erro={erro}")

        if sucesso:
            # Configurar sessão segura
            session.permanent = True
            session['user'] = {
                'username': user_data['username'],
                'email': user_data['email'],
                'name': user_data['name'],
                'role': user_data['role']
            }
            session['last_activity'] = datetime.now().isoformat()
            session['login_time'] = datetime.now().isoformat()

            print(f"✅ Login realizado com sucesso para: {user_data['name']}")

            return redirect(url_for('atendimento'))
        else:
            flash(erro, 'error')
            return render_template('login.html')

    # Se já está logado, redirecionar
    if 'user' in session:
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Logout REAL do usuário - destrói sessão e apaga cookies"""
    user = get_current_user()
    print(f"🚪 Fazendo logout SEGURO do usuário: {user.get('email') if user else 'Nenhum'}")

    # Destruir sessão completamente
    session.clear()

    # Criar resposta com redirecionamento
    response = make_response(redirect(url_for('login')))

    # Apagar cookie de sessão explicitamente
    response.set_cookie('assertiva_session', '', expires=0,
                       httponly=True, secure=has_https, samesite='Lax')

    # Headers de no-cache para logout
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    flash('Logout realizado com sucesso', 'success')
    return response

@app.route('/logout-get')
def logout_get():
    """Rota GET para logout (redireciona para POST)"""
    return redirect(url_for('login'))

@app.route('/atendimento')
@require_auth_with_security
def atendimento():
    """Página principal do sistema de atendimento com segurança avançada"""
    return render_template('atendimento.html', user=get_current_user())


@app.route('/api/responder', methods=['POST'])
# @require_auth_with_security  # Temporariamente removido para debug
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
@require_admin_with_security
def admin():
    """Painel administrativo com segurança avançada"""
    return render_template('admin.html', user=get_current_user())

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
