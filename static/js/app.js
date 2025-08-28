// Sistema de Apoio ao Atendimento - JavaScript

class SistemaAtendimento {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        // Botão de enviar pergunta
        const btnEnviar = document.getElementById('btnEnviar');
        if (btnEnviar) {
            btnEnviar.addEventListener('click', () => this.enviarPergunta());
        }

        // Enter no textarea
        const perguntaInput = document.getElementById('perguntaInput');
        if (perguntaInput) {
            perguntaInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.enviarPergunta();
                }
            });
        }
    }

    async enviarPergunta() {
        const perguntaInput = document.getElementById('perguntaInput');
        const pergunta = perguntaInput.value.trim();

        if (!pergunta) {
            alert('Digite uma pergunta válida');
            return;
        }

        this.mostrarLoading(true);

        try {
            const response = await fetch('/gerar_resposta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pergunta: pergunta })
            });

            const data = await response.json();

            if (response.ok) {
                this.exibirResposta(pergunta, data.resposta);
                perguntaInput.value = '';
            } else {
                alert('Erro: ' + data.erro);
            }
        } catch (error) {
            alert('Erro de conexão: ' + error.message);
        } finally {
            this.mostrarLoading(false);
        }
    }

    exibirResposta(pergunta, resposta) {
        const container = document.getElementById('respostasContainer');

        // Limpar formatação de conversa da resposta
        let respostaLimpa = resposta;

        // Remover saudações e formatação de conversa
        respostaLimpa = respostaLimpa.replace(/^(Olá[^!]*!?\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Oi[^!]*!?\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Bom dia[^!]*!?\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Boa tarde[^!]*!?\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Boa noite[^!]*!?\s*)/i, '');

        // Remover padrões de resposta conversacional
        respostaLimpa = respostaLimpa.replace(/^(Resposta:\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Aqui está a resposta:\s*)/i, '');
        respostaLimpa = respostaLimpa.replace(/^(Segue a resposta:\s*)/i, '');

        // Remover fechamentos conversacionais
        respostaLimpa = respostaLimpa.replace(/\s*(Espero ter ajudado[^.]*\.?\s*)$/i, '');
        respostaLimpa = respostaLimpa.replace(/\s*(Qualquer dúvida[^.]*\.?\s*)$/i, '');
        respostaLimpa = respostaLimpa.replace(/\s*(Estou à disposição[^.]*\.?\s*)$/i, '');

        // Limpar espaços extras
        respostaLimpa = respostaLimpa.trim();

        const timestamp = new Date().toLocaleString('pt-BR');

        const respostaHtml = `
            <div class="response-card fade-in">
                <div class="response-header">
                    <div>
                        <strong>📝 Resposta Gerada</strong>
                        <small class="d-block opacity-75">${timestamp}</small>
                    </div>
                    <button class="btn-copy" onclick="copiarResposta(this)">
                        📋 Copiar Tudo
                    </button>
                </div>
                <div class="response-content">${respostaLimpa.replace(/\n/g, '<br>')}</div>
            </div>
        `;

        container.innerHTML = respostaHtml + container.innerHTML;
    }

    mostrarLoading(show) {
        const loading = document.getElementById('loading');
        const btnEnviar = document.getElementById('btnEnviar');

        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }

        if (btnEnviar) {
            btnEnviar.disabled = show;
            btnEnviar.innerHTML = show ?
                '<div class="spinner-border spinner-border-sm me-2"></div>Processando...' :
                '🚀 Gerar Resposta Profissional';
        }
    }
}

// Função global para copiar resposta completa
function copiarResposta(btn) {
    const responseCard = btn.closest('.response-card');
    const respostaContent = responseCard.querySelector('.response-content');
    const texto = respostaContent.textContent.trim();

    navigator.clipboard.writeText(texto).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copiado!';
        btn.style.background = 'rgba(40, 167, 69, 0.3)';

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = 'rgba(255, 255, 255, 0.2)';
        }, 2000);
    }).catch(err => {
        console.error('Erro ao copiar:', err);
        alert('Erro ao copiar texto');
    });
}

// Função para usar exemplo
function usarExemplo(pergunta) {
    const perguntaInput = document.getElementById('perguntaInput');
    if (perguntaInput) {
        perguntaInput.value = pergunta;
        perguntaInput.focus();

        // Scroll suave para o campo de pergunta
        perguntaInput.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new SistemaAtendimento();
});