# 🚀 Sistema Local Completo - IA Atendimento Assertiva

## 📋 Visão Geral

Este é um sistema completo de atendimento com IA, extraído e otimizado para funcionar 100% localmente. Inclui autenticação segura, interface profissional, integração com OpenAI e base de conhecimento especializada.

**🎯 Objetivo:** Fornecer um ambiente de desenvolvimento/teste local para o sistema de IA de atendimento, sem dependências de AWS ou serviços externos.

## 🏗️ Arquitetura do Sistema

### 📁 Estrutura de Arquivos
```
sistema_local_simples/
├── app_simples.py              # Aplicação Flask principal
├── sistema_apoio_atendimento.py # Motor de IA e processamento
├── .env                        # Variáveis de ambiente (OpenAI)
├── requirements.txt            # Dependências Python
├── run_local.sh               # Script de execução automática
├── README.md                  # Esta documentação
├── templates/                 # Templates HTML
│   ├── base.html             # Template base com navegação
│   ├── login.html            # Página de login
│   └── atendimento.html      # Interface principal
├── static/                   # Recursos estáticos
│   ├── css/style.css        # Estilos principais
│   ├── js/app.js           # JavaScript (desabilitado)
│   └── assets/             # Imagens e ícones
└── GUIAS_PRATICOS_ASSERTIVA/ # Base de conhecimento (19 guias)
    ├── 01_acesso_sistema.md
    ├── 02_boletos.md
    └── ... (17 outros guias)
```

### 🔧 Componentes Principais

1. **Flask Application (`app_simples.py`)**
   - Servidor web principal
   - Sistema de autenticação local
   - Rotas protegidas e APIs
   - Gerenciamento de sessões

2. **Motor de IA (`sistema_apoio_atendimento.py`)**
   - Integração com OpenAI GPT
   - Processamento de base de conhecimento
   - Geração de respostas contextualizadas

3. **Interface Web (`templates/` + `static/`)**
   - Design responsivo e profissional
   - Mensagens interativas
   - Feedback visual em tempo real

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+ instalado
- Acesso à internet (para OpenAI API)
- Terminal/Command Prompt

### Opção 1: Execução Automática (Recomendada)
```bash
# Navegar para o diretório
cd sistema_local_simples

# Executar script automático
./run_local.sh
```

### Opção 2: Execução Manual
```bash
# Navegar para o diretório
cd sistema_local_simples

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python3 app_simples.py
```

### Opção 3: Ambiente Virtual (Produção)
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app_simples.py
```

## 🌐 Acesso ao Sistema

### URLs de Acesso
- **Principal:** http://localhost:8080
- **Login:** http://localhost:8080/login
- **Atendimento:** http://localhost:8080/atendimento

### 🔐 Credenciais de Acesso
- **Email:** `leandro.albertini@assertivasolucoes.com.br`
- **Senha:** `@Certificado123`

### 🔑 Configuração de Usuários
Os usuários estão definidos em `app_simples.py` na variável `USERS_DB`:
```python
USERS_DB = {
    "leandro.albertini@assertivasolucoes.com.br": {
        "password_hash": "d9af2ff511d8d1fdbcc4d2703f9cbeced5ed5e7e3b209bcececc4ea171aeb8ef",
        "name": "Leandro Albertini",
        "role": "admin"
    }
}
```

## ✨ Funcionalidades Implementadas

### 🔐 Sistema de Autenticação
- **Login Seguro:** Email + senha com hash SHA256
- **Sessões Persistentes:** 8 horas de duração
- **Tokens Únicos:** UUID para cada sessão
- **Validação Rigorosa:** Verificação em todas as rotas
- **Logout Seguro:** Limpeza completa de sessão

### 🤖 Motor de IA
- **OpenAI Integration:** GPT para geração de respostas
- **Base de Conhecimento:** 19 guias práticos carregados
- **Processamento Contextual:** Busca relevante por similaridade
- **Respostas Personalizadas:** Adaptadas ao contexto Assertiva

### 🎨 Interface de Usuário
- **Design Responsivo:** Funciona em desktop e mobile
- **Mensagens Elegantes:** Feedback visual sem pop-ups
- **Animações Suaves:** Transições CSS profissionais
- **Atalhos de Teclado:** Ctrl+Enter para gerar resposta

### 🛡️ Segurança Avançada
- **Anti-Cache:** Prevenção de acesso após logout
- **Headers Seguros:** Proteção contra XSS e clickjacking
- **Validação de Sessão:** Verificação contínua de autenticidade
- **Proteção de Rotas:** Decorators para controle de acesso

## 🔧 Dependências Técnicas

### Python Packages
```txt
Flask==2.3.3          # Framework web
openai==1.3.0          # API OpenAI
python-dotenv==1.0.0   # Gerenciamento de variáveis
```

### Variáveis de Ambiente (.env)
```env
OPENAI_API_KEY=sk-...  # Chave da API OpenAI (já configurada)
```

## 🎯 Fluxo de Uso Completo

### 1. Acesso Inicial
1. Abrir http://localhost:8080
2. Sistema redireciona para /login
3. Inserir credenciais válidas
4. Redirecionamento para /atendimento

### 2. Uso da IA
1. Digite pergunta no campo de texto
2. Clique "🚀 Gerar Resposta Profissional" ou Ctrl+Enter
3. Aguarde processamento (loading spinner)
4. Visualize resposta gerada
5. Use botão "📋 Copiar Texto" se necessário

### 3. Logout Seguro
1. Clique no botão "🚪 Sair" (destacado em vermelho)
2. Veja feedback visual "⏳ Saindo..."
3. Redirecionamento automático para login
4. Sessão completamente invalidada

## 🚨 Tratamento de Erros

### Mensagens de Erro Elegantes
- **Campo vazio:** "❌ Digite uma pergunta primeiro!" (warning)
- **Erro de API:** "❌ Erro: [detalhes]" (danger)
- **Sessão expirada:** "Sua sessão expirou. Faça login novamente." (warning)
- **Sucesso:** "✅ Resposta gerada com sucesso!" (success)

### Logs Detalhados
O sistema gera logs completos no terminal:
```
✅ Sistema de Apoio ao Atendimento inicializado
📚 19 guias práticos carregados
🎯 Pronto para gerar respostas de atendimento!
🔐 Tentando autenticar: user@email.com
✅ Login realizado com sucesso para: Nome Usuario
🔍 [APOIO] Iniciando geração de resposta para: 'pergunta'
🤖 [APOIO] Enviando requisição para OpenAI...
✅ [APOIO] Resposta recebida da OpenAI com sucesso!
🚪 Fazendo logout SEGURO do usuário: user@email.com
```

## 🛡️ Segurança Implementada

### Autenticação e Sessões
- **Hash SHA256:** Senhas nunca armazenadas em texto plano
- **Session Tokens:** UUID únicos para cada login
- **Expiração:** Sessões expiram automaticamente em 8 horas
- **Validação:** Verificação contínua de validade da sessão

### Proteção Anti-Cache
```javascript
// Headers HTTP
Cache-Control: no-cache, no-store, must-revalidate, private
Pragma: no-cache
Expires: 0
Clear-Site-Data: "cache", "cookies", "storage"

// JavaScript
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.reload(); // Força reload se vier do cache
    }
});
```

### Headers de Segurança
```python
response.headers['X-Frame-Options'] = 'DENY'
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-XSS-Protection'] = '1; mode=block'
```

### Decorators de Proteção
```python
@login_required          # Para páginas HTML
@api_login_required     # Para APIs (retorna JSON)
```

## 🔍 Debugging e Troubleshooting

### Problemas Comuns

1. **Porta 8080 ocupada:**
   ```bash
   # Verificar processo usando a porta
   lsof -i :8080
   # Matar processo se necessário
   kill -9 [PID]
   ```

2. **Dependências não instaladas:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **OpenAI API não funciona:**
   - Verificar chave no arquivo `.env`
   - Confirmar saldo na conta OpenAI
   - Testar conectividade com internet

4. **Logout não funciona:**
   - Verificar logs no terminal
   - Abrir DevTools do navegador (F12)
   - Procurar erros JavaScript no console

### Logs de Debug
Para ativar logs detalhados, modificar `app_simples.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 🚀 Customização e Extensão

### Adicionar Novos Usuários
Editar `USERS_DB` em `app_simples.py`:
```python
USERS_DB = {
    "novo@email.com": {
        "password_hash": hashlib.sha256("nova_senha".encode()).hexdigest(),
        "name": "Novo Usuario",
        "role": "user"
    }
}
```

### Modificar Base de Conhecimento
1. Adicionar arquivos `.md` em `GUIAS_PRATICOS_ASSERTIVA/`
2. Reiniciar aplicação para recarregar guias
3. Sistema carregará automaticamente novos arquivos

### Personalizar Interface
- **CSS:** Modificar `static/css/style.css`
- **HTML:** Editar templates em `templates/`
- **JavaScript:** Adicionar scripts em `templates/base.html`

### Configurar Porta Diferente
Modificar `app_simples.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Nova porta
```

## 📊 Monitoramento e Performance

### Métricas do Sistema
- **Tempo de resposta IA:** ~3-10 segundos
- **Guias carregados:** 19 arquivos
- **Memória:** ~50-100MB
- **CPU:** Baixo uso (picos durante IA)

### Otimizações Implementadas
- **Cache de guias:** Carregamento único na inicialização
- **Sessões eficientes:** Validação rápida com tokens
- **Headers otimizados:** Redução de requisições desnecessárias
- **JavaScript assíncrono:** Interface responsiva

## 🎯 Casos de Uso

### Desenvolvimento
- Testar funcionalidades sem AWS
- Desenvolver novas features
- Debug de problemas
- Prototipagem rápida

### Demonstração
- Apresentações para clientes
- Treinamento de equipe
- Validação de conceitos
- Testes de usabilidade

### Produção Local
- Ambiente isolado
- Dados sensíveis locais
- Sem dependência de internet (exceto OpenAI)
- Controle total do ambiente

## 📝 Notas Importantes

### Limitações
- **OpenAI API:** Requer internet e chave válida
- **Usuários:** Limitado aos definidos em código
- **Persistência:** Dados não persistem entre reinicializações
- **Escalabilidade:** Adequado para uso local/desenvolvimento

### Recomendações
- **Backup:** Fazer backup do arquivo `.env`
- **Segurança:** Não expor em redes públicas
- **Monitoramento:** Acompanhar logs para debug
- **Atualizações:** Manter dependências atualizadas

## 🆘 Suporte

### Para Outras IAs
Este README foi escrito especificamente para permitir que outras IAs:
1. **Compreendam** a arquitetura completa
2. **Executem** o sistema sem dificuldades
3. **Debuguem** problemas comuns
4. **Estendam** funcionalidades conforme necessário

### Informações de Contato
- **Sistema original:** Assertiva Soluções
- **Versão local:** Extraída e otimizada para desenvolvimento
- **Última atualização:** Agosto 2025

---

**🎉 Sistema pronto para uso! Execute `./run_local.sh` e acesse http://localhost:8080**
