/* app.js - JavaScript global do Sistema Assertiva */

// === SIDEBAR TOGGLE DESABILITADO ===
function toggleSidebar() {
    console.log('🚫 Toggle da sidebar foi DESABILITADO para manter sempre visível');
    // Função desabilitada - sidebar sempre expandida
    return false;
}

// Função para expandir sidebar automaticamente quando clicar em item do menu
function expandSidebarOnNavClick() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (sidebar && mainContent && sidebar.classList.contains('collapsed')) {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
    }
}

// Auto-hide sidebar on mobile when clicking outside
document.addEventListener('click', function(event) {
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        const mobileToggle = document.querySelector('.mobile-toggle');

        if (sidebar && mobileToggle && 
            !sidebar.contains(event.target) && 
            !mobileToggle.contains(event.target)) {
            sidebar.classList.remove('show');
        }
    }
});

// === LOGOUT FUNCTION ===
function fazerLogout() {
    console.log('🚪 Iniciando logout...');

    // Feedback visual imediato
    const logoutLink = document.querySelector('.logout-link');
    if (logoutLink) {
        logoutLink.innerHTML = '<div class="nav-icon">⏳</div><span class="nav-text">Saindo...</span>';
        logoutLink.style.pointerEvents = 'none';
    }

    // Desabilitar temporariamente os scripts de segurança
    window.logoutInProgress = true;

    // Limpar dados do navegador imediatamente
    if (typeof(Storage) !== "undefined") {
        localStorage.clear();
        sessionStorage.clear();
    }

    // Fazer logout via POST
    console.log('🌐 Fazendo logout via POST...');
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(() => {
        console.log('✅ Logout realizado, redirecionando...');
        window.location.href = '/login';
    }).catch(() => {
        console.log('⚠️ Erro no logout, redirecionando mesmo assim...');
        window.location.href = '/login';
    });
}

// === SECURITY SCRIPTS ===
// Detectar quando a página é carregada do cache (botão voltar)
window.addEventListener('pageshow', function(event) {
    // Não interferir se logout está em progresso
    if (window.logoutInProgress) return;

    if (event.persisted) {
        // Página foi carregada do cache - forçar reload
        window.location.reload();
    }
});

// Detectar navegação pelo histórico
window.addEventListener('popstate', function() {
    // Não interferir se logout está em progresso
    if (window.logoutInProgress) return;

    // Verificar se ainda está autenticado fazendo uma requisição
    fetch('/', {
        method: 'GET',
        cache: 'no-cache',
        headers: {
            'Cache-Control': 'no-cache'
        }
    }).then(response => {
        if (response.redirected && response.url.includes('/login')) {
            // Não está mais autenticado - redirecionar
            window.location.href = '/login';
        }
    }).catch(() => {
        // Erro - redirecionar para login
        window.location.href = '/login';
    });
});

// Prevenir cache da página
if (window.history && window.history.pushState) {
    window.addEventListener('beforeunload', function() {
        // Limpar cache ao sair da página
        if ('caches' in window) {
            caches.keys().then(function(names) {
                names.forEach(function(name) {
                    caches.delete(name);
                });
            });
        }
    });
}

// === INICIALIZAÇÃO ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema Assertiva carregado');

    // Event listeners do toggle foram REMOVIDOS para manter sidebar sempre visível
    console.log('🚫 Event listeners do toggle foram DESABILITADOS');
    console.log('✅ Sidebar permanecerá sempre expandida');

    // Adicionar event listeners para expandir sidebar ao clicar em itens do menu
    const navLinks = document.querySelectorAll('.sidebar .nav-link:not(.logout-link):not(.nav-link-disabled)');
    navLinks.forEach(link => {
        link.addEventListener('click', expandSidebarOnNavClick);
    });

    // Init Lucide - removido para evitar conflito com base.html
    // A inicialização do Lucide agora é feita apenas no base.html

    // Debug dos ícones
    console.log('🔍 DEBUG: Verificando ícones Lucide...');

    // Verificar ícones na página
    const icons = document.querySelectorAll('i[data-lucide]');
    console.log('🔍 Ícones Lucide encontrados:', icons.length);

    icons.forEach((icon, index) => {
        console.log(`🔍 Ícone ${index + 1}:`, icon.getAttribute('data-lucide'), 'Elemento:', icon.tagName);
    });

    // Configurar logout link se existir
    const logoutLink = document.querySelector('.logout-link');
    if (logoutLink) {
        console.log('✅ Botão logout encontrado e configurado');
    } else {
        console.log('ℹ️ Botão logout não encontrado (normal em páginas públicas)');
    }
});

// === UTILITY FUNCTIONS ===
// Função para mostrar mensagens
function mostrarMensagem(texto, tipo = 'info', duracao = 5000) {
    // Criar elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${texto}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Inserir no topo da página
    const mainContent = document.querySelector('.content-inner') || document.querySelector('main');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
    }

    // Auto-remover após duração especificada
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duracao);
}

// Função para loading spinner
function showLoading(element, text = 'Carregando...') {
    if (element) {
        element.disabled = true;
        element.innerHTML = `<i class="spinner-border spinner-border-sm me-2" role="status"></i>${text}`;
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}
