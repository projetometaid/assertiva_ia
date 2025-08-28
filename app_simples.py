from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response
from sistema_apoio_atendimento import SistemaApoioAtendimento
import os
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'dev-secret-key-local-sistema-apoio-2024'
app.permanent_session_lifetime = timedelta(hours=8)  # Sessão expira em 8 horas

# Base de usuários local
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
    """Decorator para rotas que requerem login com validação de sessão"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_session_validity():
            invalidate_session()
            flash('Sua sessão expirou. Faça login novamente.', 'warning')
            return redirect(url_for('login'))

        # Adicionar headers de segurança
        response = make_response(f(*args, **kwargs))
        return add_security_headers(response)
    return decorated_function

def api_login_required(f):
    """Decorator para APIs que requerem login - retorna JSON em caso de erro"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_session_validity():
            invalidate_session()
            return jsonify({'error': 'Sessão expirada. Faça login novamente.'}), 401

        # Adicionar headers de segurança
        response = make_response(f(*args, **kwargs))
        return add_security_headers(response)
    return decorated_function

def api_login_required(f):
    """Decorator para APIs que requerem login - retorna JSON em caso de erro"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_session_validity():
            invalidate_session()
            return jsonify({'error': 'Sessão expirada. Faça login novamente.'}), 401

        # Adicionar headers de segurança
        response = make_response(f(*args, **kwargs))
        return add_security_headers(response)
    return decorated_function

def get_current_user():
    """Retorna dados do usuário atual da sessão"""
    return session.get('user', None)

def check_session_validity():
    """Verifica se a sessão é válida e não expirou"""
    if 'user' not in session:
        return False

    # Verificar se tem token de sessão
    if 'session_token' not in session:
        return False

    # Verificar tempo de login
    if 'login_time' not in session:
        return False

    try:
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.now() - login_time > timedelta(hours=8):
            return False
    except:
        return False

    return True

def invalidate_session():
    """Invalida completamente a sessão"""
    session.clear()
    session.permanent = False

def add_security_headers(response):
    """Adiciona headers de segurança para prevenir cache"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Sistema de apoio
sistema_apoio = SistemaApoioAtendimento()

@app.route('/')
def index():
    """Página inicial - verifica sessão válida"""
    if not check_session_validity():
        invalidate_session()
        return redirect(url_for('login'))

    response = make_response(redirect(url_for('atendimento')))
    return add_security_headers(response)

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

        # Tentar autenticar
        sucesso, user_data, erro = authenticate_user(email, password)
        print(f"🔐 Resultado autenticação: sucesso={sucesso}, erro={erro}")

        if sucesso:
            # Configurar sessão segura
            session.permanent = True
            session['user'] = user_data
            session['login_time'] = datetime.now().isoformat()
            session['session_token'] = str(uuid.uuid4())  # Token único da sessão

            print(f"✅ Login realizado com sucesso para: {user_data['name']}")
            flash(f'Bem-vindo, {user_data["name"]}!', 'success')

            # Criar resposta com headers de segurança
            response = make_response(redirect(url_for('atendimento')))
            return add_security_headers(response)
        else:
            print(f"❌ Falha no login: {erro}")
            flash(erro, 'error')
            return render_template('login.html')

    # Se já está logado com sessão válida, redireciona
    if check_session_validity():
        response = make_response(redirect(url_for('atendimento')))
        return add_security_headers(response)

    # Limpar qualquer sessão inválida
    invalidate_session()

    # Renderizar página de login com headers de segurança
    response = make_response(render_template('login.html'))
    return add_security_headers(response)

@app.route('/logout', methods=['POST'])
def logout():
    """Logout SEGURO do usuário - destrói sessão e previne cache"""
    user = get_current_user()
    print(f"🚪 Fazendo logout SEGURO do usuário: {user.get('email') if user else 'Nenhum'}")

    # Invalidar sessão completamente
    invalidate_session()

    # Criar resposta com headers anti-cache
    response = make_response(redirect(url_for('login')))

    # Headers para forçar limpeza de cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'

    # Adicionar outros headers de segurança
    response = add_security_headers(response)

    flash('Logout realizado com sucesso', 'success')
    return response

@app.route('/logout-get')
def logout_get():
    """Rota GET para logout (redireciona para login com limpeza)"""
    invalidate_session()
    response = make_response(redirect(url_for('login')))
    return add_security_headers(response)

@app.route('/atendimento')
@login_required
def atendimento():
    """Página de atendimento - requer login"""
    user = get_current_user()
    return render_template('atendimento.html', user=user, username=user['name'])

@app.route('/gerar_resposta', methods=['POST'])
@api_login_required
def gerar_resposta():
    """Gerar resposta - requer login"""
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '')

        if not pergunta.strip():
            return jsonify({'error': 'Pergunta não pode estar vazia'}), 400

        resposta = sistema_apoio.gerar_resposta_atendimento(pergunta)
        return jsonify({'resposta': resposta})

    except Exception as e:
        return jsonify({'error': f'Erro ao gerar resposta: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
