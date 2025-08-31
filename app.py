"""
Sistema Assertiva IA - Arquitetura Organizada
"""
import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS

# Importar configurações
from config.settings import IS_PRODUCTION, VITE_ORIGIN

# Importar blueprints
from routes.web import web
from routes.api import api

# Importar stores para inicialização
from stores.user_store import ensure_admin_user
from stores.invite_store import cleanup_expired_invites

# Importar sistema de apoio
import sys
sys.path.append('.')
from sistema_apoio_atendimento import SistemaApoioAtendimento


def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações de segurança
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SESSION_COOKIE_SECURE=IS_PRODUCTION,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_NAME='assertiva_session',
        # Desenvolvedor: garanta recarregamento de templates e assets em DEV
        TEMPLATES_AUTO_RELOAD=not IS_PRODUCTION,
        SEND_FILE_MAX_AGE_DEFAULT=0 if not IS_PRODUCTION else 31536000
    )
    
    # CORS apenas para origem específica
    CORS(app, origins=[VITE_ORIGIN], supports_credentials=True)
    
    # Headers de segurança
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP básica
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    # Middleware de no-cache para páginas protegidas
    @app.before_request
    def add_no_cache():
        from flask import request
        protected_paths = ['/atendimento', '/configuracoes', '/api/']
        
        if any(request.path.startswith(path) for path in protected_paths):
            response = make_response()
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Surrogate-Control'] = 'no-store'
    
    # Registrar blueprints
    app.register_blueprint(web)
    app.register_blueprint(api)
    
    # Rota de health check
    @app.route('/health')
    def health():
        """Health check para monitoramento"""
        return jsonify({
            'status': 'healthy',
            'sistema_apoio': sistema_apoio is not None,
            'build_version': '1.0.0',
            'uptime': 'TODO: implementar uptime'
        })
    
    return app


# Inicializar sistema de apoio
print("🔧 Inicializando Sistema de Apoio ao Atendimento...")
try:
    sistema_apoio = SistemaApoioAtendimento()
    print("✅ Sistema de Apoio ao Atendimento inicializado")
except Exception as e:
    print(f"❌ Erro ao inicializar sistema de apoio: {str(e)}")
    sistema_apoio = None

# Criar aplicação
app = create_app()

# Rota de teste para Lucide
@app.route('/teste-lucide')
def teste_lucide():
    from flask import render_template
    return render_template('teste_lucide.html')

# Adicionar rota de resposta IA
@app.route('/api/responder', methods=['POST'])
def api_responder():
    """API para gerar resposta com IA"""
    from flask import request, jsonify
    from security.auth import require_auth, get_current_user
    
    @require_auth
    def _responder():
        try:
            if not sistema_apoio:
                return jsonify({'erro': 'Sistema de apoio não disponível'}), 503
            
            data = request.get_json()
            pergunta = data.get('pergunta', '').strip()
            
            if not pergunta:
                return jsonify({'erro': 'Pergunta é obrigatória'}), 400
            
            print(f"🔄 [LOG] Iniciando processamento da pergunta...")
            print(f"📥 [LOG] Dados recebidos: {data}")
            print(f"❓ [LOG] Pergunta extraída: '{pergunta}'")
            
            # Gerar resposta
            resposta = sistema_apoio.gerar_resposta_atendimento(pergunta)
            
            if not resposta:
                return jsonify({'erro': 'Não foi possível gerar resposta'}), 500
            
            print(f"✅ [LOG] Resposta gerada com sucesso: {len(resposta)} caracteres")
            
            return jsonify({
                'sucesso': True,
                'resposta': resposta,
                'pergunta': pergunta
            })
            
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {str(e)}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    return _responder()


if __name__ == '__main__':
    # Inicializar dados
    print("🔧 Inicializando dados do sistema...")
    ensure_admin_user()
    cleanup_expired_invites()
    print("✅ Sistema inicializado com sucesso!")
    
    # Executar aplicação
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
