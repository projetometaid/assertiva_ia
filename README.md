# 🤖 Sistema Assertiva IA - Apoio ao Atendimento

## 📋 Visão Geral

Sistema completo de apoio ao atendimento com IA, gestão de usuários, autenticação JWT e interface moderna. Inclui sistema de convites, RBAC (Role-Based Access Control) e integração com OpenAI.

**🎯 Objetivo:** Sistema profissional de atendimento com IA, pronto para produção com todas as funcionalidades de segurança e gestão.

## 🏗️ Arquitetura do Sistema

### 📁 Estrutura de Arquivos
```
assertiva_ia/
├── app.py                      # Aplicação Flask principal
├── sistema_apoio_atendimento.py # Motor de IA e processamento
├── .env                        # Variáveis de ambiente
├── .env.example               # Exemplo de configuração
├── requirements.txt            # Dependências Python
├── README.md                  # Esta documentação
├── data/                      # Dados do sistema
│   ├── users.json            # Base de usuários
│   └── invites.json          # Convites pendentes
├── templates/                 # Templates HTML
│   ├── base.html             # Template base com navegação
│   ├── login.html            # Página de login
│   ├── atendimento.html      # Interface principal
│   ├── configuracoes.html    # Gestão de usuários
│   └── convite.html          # Aceitar convites
├── static/                   # Recursos estáticos
│   ├── css/style.css        # Estilos principais
│   ├── js/                  # Scripts JavaScript
│   └── assets/              # Imagens, ícones, etc.
└── GUIAS_PRATICOS_ASSERTIVA/ # Base de conhecimento (19 guias)
    ├── 00_INDICE_GUIAS_PRATICOS.md
    └── *.md                 # Guias em Markdown
```

### 🔧 Componentes Principais

1. **Flask Application (`app.py`)**
   - Servidor web com JWT
   - Autenticação segura
   - RBAC (admin/atendente)
   - Sistema de convites

2. **Motor de IA (`sistema_apoio_atendimento.py`)**
   - Integração com OpenAI GPT
   - Processamento de base de conhecimento
   - Geração de respostas contextualizadas

3. **Interface Web (`templates/` + `static/`)**
   - Design moderno e responsivo
   - Gestão de usuários
   - Sistema de configurações

4. **Base de Conhecimento**
   - 19 guias práticos em Markdown
   - Busca semântica automática
   - Contexto especializado Assertiva

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+ instalado
- Acesso à internet (para OpenAI API)
- Terminal/Command Prompt

### Execução
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Executar o sistema
python3 app.py
```

**🌐 Acesso:** http://127.0.0.1:5001

### Ambiente Virtual (Recomendado)
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
python3 app.py
```

## 🌐 Acesso ao Sistema

### URLs de Acesso
- **Principal:** http://127.0.0.1:5001
- **Login:** http://127.0.0.1:5001/login
- **Atendimento:** http://127.0.0.1:5001/atendimento
- **Configurações:** http://127.0.0.1:5001/configuracoes

### 🔐 Credenciais Iniciais
- **Email:** `admin@assertiva.local`
- **Senha:** `admin123`

### 🔑 Gestão de Usuários
- Sistema completo de gestão via interface web
- Criação de convites por link
- Roles: admin e atendente
- Dados armazenados em `data/users.json`

## ✨ Funcionalidades Implementadas

### 🔐 Sistema de Autenticação JWT
- **JWT Tokens:** Access + Refresh tokens com httpOnly cookies
- **RBAC:** Controle de acesso baseado em roles (admin/atendente)
- **Sessões Seguras:** Tokens com expiração configurável
- **Logout Seguro:** Invalidação completa de tokens

### 👥 Gestão de Usuários
- **Sistema de Convites:** Criação de links de convite únicos
- **Gestão Completa:** Listar, editar roles, excluir usuários
- **Exclusão Segura:** Soft delete com confirmação
- **Interface Admin:** Painel completo de administração

### 🤖 Motor de IA
- **OpenAI Integration:** GPT para geração de respostas
- **Base de Conhecimento:** 19 guias práticos carregados
- **Processamento Contextual:** Busca relevante por similaridade
- **Respostas Personalizadas:** Adaptadas ao contexto Assertiva

### 🎨 Interface Moderna
- **Design Responsivo:** Funciona em desktop e mobile
- **Interface Intuitiva:** Navegação clara e organizada
- **Feedback Visual:** Mensagens de status em tempo real
- **Atalhos de Teclado:** Ctrl+Enter para gerar resposta

### 🛡️ Segurança Avançada
- **Headers Seguros:** Proteção contra XSS e clickjacking
- **Validação Rigorosa:** Verificação em todas as rotas
- **Proteção CSRF:** Cookies SameSite e httpOnly
- **Criptografia:** Senhas com hash SHA256

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
1. Abrir http://127.0.0.1:5001
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
Para ativar logs detalhados, modificar `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 🚀 Customização e Extensão

### Adicionar Novos Usuários
Use o sistema de convites via interface web:
1. Acesse http://127.0.0.1:5001/configuracoes
2. Clique em "Gerar Link de Convite"
3. Insira o email do novo usuário
4. Envie o link gerado para o usuário
5. O usuário define sua própria senha

### Modificar Base de Conhecimento
1. Adicionar arquivos `.md` em `GUIAS_PRATICOS_ASSERTIVA/`
2. Reiniciar aplicação para recarregar guias
3. Sistema carregará automaticamente novos arquivos

### Personalizar Interface
- **CSS:** Modificar `static/css/style.css`
- **HTML:** Editar templates em `templates/`
- **JavaScript:** Adicionar scripts em `templates/base.html`

### Configurar Porta Diferente
Modificar `app.py`:
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
- **Sistema:** Assertiva IA - Apoio ao Atendimento
- **Versão:** Sistema completo com JWT e gestão de usuários
- **Última atualização:** Agosto 2025

---

**🎉 Sistema pronto para uso! Execute `python3 app.py` e acesse http://127.0.0.1:5001**
