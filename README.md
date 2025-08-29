# 🤖 Sistema Assertiva IA - Apoio ao Atendimento

## 📋 Visão Geral

Sistema completo de apoio ao atendimento com IA, construído com **arquitetura organizada em camadas**, autenticação JWT segura, gestão completa de usuários e interface moderna. Inclui sistema de convites, RBAC (Role-Based Access Control), integração com OpenAI e preparação para migração futura para AWS Cognito.

**🎯 Objetivo:** Sistema profissional de atendimento com IA, pronto para produção com arquitetura escalável, segurança avançada e manutenibilidade.

## 🏗️ Arquitetura do Sistema

### 📁 Nova Estrutura Organizada em Camadas
```
assertiva_ia/
├── app.py                      # 🚀 Aplicação Flask principal (Factory Pattern)
├── sistema_apoio_atendimento.py # 🤖 Motor de IA e processamento OpenAI
├── .env                        # 🔐 Variáveis de ambiente
├── .env.example               # 📋 Exemplo de configuração completo
├── requirements.txt            # 📦 Dependências Python
├── README.md                  # 📚 Esta documentação
│
├── config/                    # ⚙️ CONFIGURAÇÕES CENTRALIZADAS
│   ├── __init__.py
│   └── settings.py           # Todas as variáveis de ambiente e constantes
│
├── security/                  # 🛡️ MÓDULOS DE SEGURANÇA
│   ├── __init__.py
│   ├── auth.py              # JWT, tokens, decorators @require_auth/@require_role
│   ├── cookies.py           # Gerenciamento seguro de cookies (prod/dev)
│   └── password.py          # Werkzeug hash/verify (substitui SHA256)
│
├── stores/                    # 💾 CAMADA DE DADOS (Data Access Layer)
│   ├── __init__.py
│   ├── user_store.py        # CRUD usuários, soft delete, paginação
│   └── invite_store.py      # CRUD convites, tokens JWT, cleanup automático
│
├── services/                  # 🔧 REGRAS DE NEGÓCIO (Business Logic)
│   ├── __init__.py
│   ├── auth_service.py      # Autenticação, validações, permissões
│   └── user_service.py      # Gestão usuários, convites, validações
│
├── routes/                    # 🌐 CONTROLADORES (Blueprints)
│   ├── __init__.py
│   ├── web.py              # Rotas HTML (páginas web)
│   └── api.py              # Rotas API JSON (/api/*)
│
├── data/                      # 📊 DADOS PERSISTENTES
│   ├── users.json            # Base de usuários (Werkzeug hashes)
│   └── invites.json          # Convites pendentes (JWT tokens)
│
├── templates/                 # 🎨 TEMPLATES HTML
│   ├── base.html             # Template base com navegação
│   ├── login.html            # Página de login
│   ├── atendimento.html      # Interface principal de IA
│   ├── configuracoes.html    # Gestão de usuários (admin only)
│   └── convite.html          # Aceitar convites
│
├── static/                   # 🎭 RECURSOS ESTÁTICOS
│   ├── css/style.css        # Estilos principais (variáveis CSS)
│   ├── js/                  # Scripts JavaScript
│   └── assets/              # Imagens, ícones, favicons
│
└── GUIAS_PRATICOS_ASSERTIVA/ # 📖 BASE DE CONHECIMENTO IA
    ├── 00_INDICE_GUIAS_PRATICOS.md
    └── *.md                 # 19 guias práticos em Markdown
```

### 🔧 Arquitetura em Camadas Implementada

#### 🏗️ **1. CAMADA DE CONFIGURAÇÃO (`config/`)**
- **`settings.py`**: Centralizou TODAS as configurações
- **Paths robustos**: `BASE_DIR = Path(__file__).parent.parent`
- **Variáveis de ambiente**: JWT, convites, admin, CORS, OpenAI
- **Função `ensure_data_dir()`**: Cria diretórios automaticamente

#### 🛡️ **2. CAMADA DE SEGURANÇA (`security/`)**
- **`auth.py`**: JWT completo, decorators `@require_auth`, `@require_role`
- **`cookies.py`**: Cookies condicionais por ambiente (secure=prod)
- **`password.py`**: Werkzeug (substitui SHA256) - hash_password/verify_password
- **Blindagens**: Proteção SYSTEM_USER_ID, auto-exclusão, role próprio

#### 💾 **3. CAMADA DE DADOS (`stores/`)**
- **`user_store.py`**: CRUD completo, soft delete, paginação, ensure_admin_user
- **`invite_store.py`**: Tokens JWT, TTL configurável, cleanup automático
- **Validações**: Email duplicado, convite ativo, expiração
- **Paths seguros**: Resolve a partir do app, não CWD

#### 🔧 **4. CAMADA DE NEGÓCIO (`services/`)**
- **`auth_service.py`**: Autenticação, geração tokens, validações permissão
- **`user_service.py`**: Regras de negócio, validações email, confirmações
- **Separação clara**: Lógica de negócio isolada dos dados

#### 🌐 **5. CAMADA DE CONTROLADORES (`routes/`)**
- **`web.py`**: Blueprint HTML (páginas), redirects + flash
- **`api.py`**: Blueprint JSON (/api/*), sempre retorna JSON + HTTP codes
- **Blueprints separados**: Organização clara, prefixos automáticos

#### 🤖 **6. MOTOR DE IA (`sistema_apoio_atendimento.py`)**
- **Integração OpenAI GPT**: Processamento de perguntas
- **Base de conhecimento**: 19 guias práticos em Markdown
- **Busca semântica**: Contexto especializado Assertiva

## 🆕 Melhorias Implementadas na Nova Arquitetura

### ✅ **A) Sistema de Autenticação Limpo**
- **Removidos decorators antigos**: `login_required`, `admin_required`, `require_auth_with_security`
- **Mantido apenas JWT**: `get_current_user()` via cookies httpOnly
- **Código reduzido**: -150 linhas de código duplicado/obsoleto
- **Importações circulares**: Resolvidas com módulo `security/password.py`

### 🍪 **B) Cookies Condicionais por Ambiente**
- **Função `set_cookie()`**: Configuração automática baseada em `FLASK_ENV`
- **Produção**: `secure=True`, `httponly=True`, `samesite='Lax'`
- **Desenvolvimento**: `secure=False` para localhost
- **Simplificação**: Uma função para todos os cookies JWT

### 🔐 **C) Werkzeug para Senhas (Segurança Melhorada)**
- **Substituído SHA256**: Por `generate_password_hash()` / `check_password_hash()`
- **Salt automático**: Cada senha tem salt único
- **Compatibilidade**: Sistema detecta e migra hashes antigos
- **Aplicado em**: Login, criação de usuário, convites

### 📁 **D) Paths Robustos e Organizados**
- **pathlib.Path**: `BASE_DIR = Path(__file__).parent`
- **Variáveis centralizadas**: `DATA_DIR`, `USERS_FILE`, `INVITES_FILE`
- **Criação automática**: `ensure_data_dir()` com `mkdir(parents=True, exist_ok=True)`
- **Independente do CWD**: Funciona de qualquer diretório

### 🛡️ **E) Blindagens de Segurança Avançadas**
- **Proteção SYSTEM_USER_ID**: Não pode ser editado/excluído
- **Auto-proteção**: Usuário não pode se auto-excluir
- **Role próprio**: Não pode alterar próprio role
- **Confirmação obrigatória**: "EXCLUIR" para deletar usuários
- **Reatribuição de dados**: `reassign_or_anonymize()` antes do soft delete

### 🏗️ **F) Arquitetura em Camadas (Clean Architecture)**
- **Separação clara**: Config → Security → Stores → Services → Routes
- **Blueprints organizados**: `/api/*` JSON, páginas HTML separadas
- **Injeção de dependência**: Services usam stores, routes usam services
- **Testabilidade**: Cada camada pode ser testada independentemente
- **Manutenibilidade**: Mudanças isoladas por responsabilidade

### 🔄 **G) Sistema de Convites Robusto**
- **Tokens JWT**: Com `exp` em epoch seconds
- **TTL configurável**: `INVITE_TTL_MINUTES` via env
- **Prevenção duplicatas**: Um convite ativo por email
- **Cleanup automático**: Remove convites expirados na inicialização
- **Validação forte**: Email format, token integrity, expiração

### 📊 **H) Gestão de Usuários Completa**
- **Paginação**: `GET /api/users?limit=50&offset=0`
- **Soft delete**: `deletedAt` timestamp, dados preservados
- **RBAC granular**: Admin vs atendente, validações por endpoint
- **Auditoria**: Logs de ações sensíveis com timestamp e IP
- **Validações**: Email format, role enum, confirmações

## 🚀 Como Rodar Local

### 📋 Pré-requisitos
- **Python 3.8+** instalado
- **Git** para clonar o repositório
- **Chave OpenAI API** (obrigatória para IA)
- **Terminal/Command Prompt**

### ⚡ Execução Rápida
```bash
# 1. Clonar repositório
git clone https://github.com/projetometaid/assertiva_ia.git
cd assertiva_ia

# 2. Criar ambiente virtual (RECOMENDADO)
python3 -m venv venv

# 3. Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente
cp .env.example .env
# EDITE o arquivo .env com suas configurações

# 6. Executar o sistema
python3 app.py
```

### 🔑 Configuração Obrigatória (.env)
```bash
# Editar .env com suas configurações:
nano .env  # ou seu editor preferido

# Configurações mínimas obrigatórias:
OPENAI_API_KEY=sua-chave-openai-aqui
JWT_SECRET=sua-chave-jwt-secreta-aqui
SECRET_KEY=sua-chave-flask-secreta-aqui

# Para produção, adicionar:
FLASK_ENV=production
```

### 🌐 Acesso ao Sistema
- **URL Principal:** http://127.0.0.1:5001
- **Login Inicial:** `admin@assertiva.local` / `admin123`
- **Configurações:** http://127.0.0.1:5001/configuracoes (admin only)

## ☁️ Migração para AWS Cognito (Futuro)

### 🏗️ Infraestrutura com Terraform

O sistema foi **projetado para migração fácil** para AWS Cognito. A arquitetura em camadas permite trocar apenas o **auth_adapter** mantendo todas as rotas iguais.

#### 📁 Estrutura de Infraestrutura
```bash
# Criar estrutura Terraform
mkdir -p infra/terraform
cd infra/terraform

# Arquivos Terraform necessários:
├── main.tf              # Provider AWS, região
├── cognito.tf           # User Pool + App Client
├── variables.tf         # Variáveis de entrada
├── outputs.tf           # Exportar IDs e URLs
└── terraform.tfvars     # Valores específicos do ambiente
```

#### 🔧 Configuração Cognito (cognito.tf)
```hcl
# User Pool
resource "aws_cognito_user_pool" "assertiva_pool" {
  name = "assertiva-users"

  # Configurações de senha
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # Atributos obrigatórios
  schema {
    attribute_data_type = "String"
    name               = "email"
    required           = true
    mutable           = true
  }

  # Configurações de email
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]
}

# App Client
resource "aws_cognito_user_pool_client" "assertiva_client" {
  name         = "assertiva-app"
  user_pool_id = aws_cognito_user_pool.assertiva_pool.id

  # Configurações JWT
  access_token_validity  = 15  # minutos
  refresh_token_validity = 7   # dias

  # Fluxos permitidos
  explicit_auth_flows = [
    "ADMIN_NO_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}
```

#### 📤 Outputs (outputs.tf)
```hcl
output "user_pool_id" {
  value = aws_cognito_user_pool.assertiva_pool.id
}

output "client_id" {
  value = aws_cognito_user_pool_client.assertiva_client.id
}

output "jwks_uri" {
  value = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.assertiva_pool.id}/.well-known/jwks.json"
}
```

### � Adaptador de Autenticação

#### Estrutura do Auth Adapter
```python
# security/auth_adapter.py
class AuthAdapter:
    def authenticate(self, email, password): pass
    def create_user(self, email, temp_password): pass
    def validate_token(self, token): pass

# Implementações:
class LocalAuthAdapter(AuthAdapter):     # JSON atual
class CognitoAuthAdapter(AuthAdapter):   # AWS Cognito
```

#### Migração Cognito (cognito_adapter.py)
```python
import boto3
from botocore.exceptions import ClientError

class CognitoAuthAdapter(AuthAdapter):
    def __init__(self):
        self.cognito = boto3.client('cognito-idp')
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_CLIENT_ID')

    def create_user(self, email, role='atendente'):
        """Cria usuário no Cognito"""
        try:
            response = self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'custom:role', 'Value': role}
                ],
                MessageAction='SUPPRESS',  # Não enviar email
                TemporaryPassword=self._generate_temp_password()
            )

            # Definir senha permanente
            self.cognito.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=temp_password,
                Permanent=True
            )

            return True, None
        except ClientError as e:
            return False, str(e)

    def validate_token(self, id_token):
        """Valida ID Token com JWKs do Cognito"""
        # Implementar validação JWT com chaves públicas
        # jwks_uri do output Terraform
        pass
```

### 🚀 Comandos de Deploy

#### 1. Provisionar Infraestrutura
```bash
# Inicializar Terraform
cd infra/terraform
terraform init

# Planejar mudanças
terraform plan

# Aplicar infraestrutura
terraform apply

# Obter outputs
terraform output user_pool_id
terraform output client_id
terraform output jwks_uri
```

#### 2. Configurar Aplicação
```bash
# Adicionar ao .env
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
COGNITO_JWKS_URI=https://cognito-idp.us-east-1.amazonaws.com/...
AUTH_ADAPTER=cognito  # ou 'local'
```

#### 3. Migrar Usuários
```python
# Script de migração (migrate_to_cognito.py)
def migrate_users():
    local_users = load_users()  # JSON atual
    cognito_adapter = CognitoAuthAdapter()

    for user in local_users.values():
        if user.get('deletedAt') is None:
            success, error = cognito_adapter.create_user(
                user['email'],
                user['role']
            )
            if success:
                print(f"✅ Migrado: {user['email']}")
            else:
                print(f"❌ Erro: {user['email']} - {error}")
```

### ✅ Vantagens da Migração
- **Escalabilidade**: Suporta milhões de usuários
- **Segurança**: MFA, detecção de anomalias, compliance
- **Manutenção**: Zero manutenção de infraestrutura auth
- **Integração**: SSO, SAML, OAuth2, redes sociais
- **Auditoria**: CloudTrail automático
- **Backup**: Dados replicados automaticamente

### 🔄 Compatibilidade Total
- **Mesmas rotas**: `/api/login`, `/api/users`, etc.
- **Mesma interface**: Nenhuma mudança no frontend
- **Mesmos roles**: admin/atendente preservados
- **Migração gradual**: Pode rodar ambos em paralelo

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

## 🧪 Desenvolvimento e Testes

### 📋 Testes Recomendados
```bash
# Instalar dependências de teste
pip install pytest pytest-flask pytest-cov

# Estrutura de testes sugerida:
tests/
├── test_auth.py          # Testes de autenticação
├── test_users.py         # Testes de gestão de usuários
├── test_invites.py       # Testes de convites
├── test_api.py           # Testes de endpoints API
└── test_security.py      # Testes de segurança

# Executar testes
pytest tests/ -v --cov=.
```

### 🔧 Qualidade de Código
```bash
# Instalar ferramentas de qualidade
pip install black isort flake8 pre-commit

# Configurar pre-commit
pre-commit install

# Formatação automática
black .
isort .
flake8 .
```

### 📊 Monitoramento de Produção
```bash
# Health check endpoint
curl http://127.0.0.1:5001/health

# Response esperado:
{
  "status": "healthy",
  "sistema_apoio": true,
  "build_version": "1.0.0",
  "uptime": "TODO: implementar uptime"
}
```

### 🚀 Deploy de Produção
```bash
# Usar WSGI server (não Flask dev server)
pip install gunicorn

# Executar com Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app

# Ou com Docker (Dockerfile sugerido):
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## 📞 Suporte e Contribuição

### 🤝 Como Contribuir
1. **Fork** o repositório
2. **Crie branch** para sua feature: `git checkout -b feature/nova-funcionalidade`
3. **Commit** suas mudanças: `git commit -m 'feat: adiciona nova funcionalidade'`
4. **Push** para branch: `git push origin feature/nova-funcionalidade`
5. **Abra Pull Request** com descrição detalhada

### 📧 Contato
- **Email:** leandro.albertini@metaid.com.br
- **Repositório:** https://github.com/projetometaid/assertiva_ia
- **Issues:** Para bugs e sugestões de melhorias

### 📝 Convenções de Commit
```bash
feat: nova funcionalidade
fix: correção de bug
docs: atualização de documentação
style: formatação, sem mudança de lógica
refactor: refatoração de código
test: adição ou correção de testes
chore: tarefas de manutenção
```

---

**� Sistema Assertiva IA - Arquitetura moderna, segurança avançada e pronto para escalar!**

*Desenvolvido com ❤️ pela equipe MetaID*
