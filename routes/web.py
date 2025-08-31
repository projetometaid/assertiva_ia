"""
Rotas HTML (páginas web)
"""
from flask import Blueprint, render_template, request, redirect, url_for, make_response, jsonify

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
    user = get_current_user()
    response = make_response(render_template('atendimento.html', user=user))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@web.route('/configuracoes')
@require_role('admin')
def configuracoes():
    """Página de configurações (apenas admin)"""
    user = get_current_user()
    return render_template('configuracoes.html', user=user)


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
        return redirect(url_for('web.login'))

    # Validar token
    valid, email, error = validate_invite_token(token)
    if not valid:
        return redirect(url_for('web.login'))

    return render_template('convite.html', token=token, email=email)



