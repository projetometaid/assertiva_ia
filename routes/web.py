"""
Rotas HTML (páginas web)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response

from security.auth import require_auth, require_role, get_current_user
from security.cookies import clear_auth_cookies
from stores.invite_store import validate_invite_token

web = Blueprint('web', __name__)


@web.route('/')
def index():
    """Página inicial - redireciona para atendimento se logado"""
    user = get_current_user()
    if user:
        return redirect(url_for('web.atendimento'))
    return redirect(url_for('web.login'))


@web.route('/login')
def login():
    """Página de login"""
    user = get_current_user()
    if user:
        return redirect(url_for('web.atendimento'))
    return render_template('login.html')


@web.route('/atendimento')
@require_auth
def atendimento():
    """Página principal de atendimento"""
    return render_template('atendimento.html')


@web.route('/configuracoes')
@require_role('admin')
def configuracoes():
    """Página de configurações (apenas admin)"""
    return render_template('configuracoes.html')


@web.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout - redireciona para página de login"""
    response = make_response(redirect(url_for('web.login')))
    clear_auth_cookies(response)
    print("✅ Logout realizado")
    return response


@web.route('/convite')
def convite():
    """Página para aceitar convite"""
    token = request.args.get('token')
    if not token:
        flash('Token de convite não encontrado', 'error')
        return redirect(url_for('web.login'))

    # Validar token
    valid, email, error = validate_invite_token(token)
    if not valid:
        flash(f'Convite inválido: {error}', 'error')
        return redirect(url_for('web.login'))

    return render_template('convite.html', token=token, email=email)


@web.route('/users')
@require_role('admin')
def users():
    """Redireciona para API de usuários (compatibilidade)"""
    return redirect(url_for('api.list_users'))
