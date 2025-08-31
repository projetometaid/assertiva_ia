# Problema: Loop Infinito no Login - Sistema Assertiva IA

## 📋 Resumo do Problema

O usuário estava enfrentando um **loop infinito no login** onde:
- Digitava email e senha corretamente
- Sistema processava o login
- Redirecionava de volta para a tela de login
- Mostrava mensagem: "Você precisa fazer login para acessar esta página"
- Processo se repetia indefinidamente

## 🔍 Diagnóstico

### Problema Principal
Os **cookies de autenticação estavam sendo definidos com o flag `Secure`**, que só funciona com conexões HTTPS. Como o sistema estava sendo acessado via HTTP através do Load Balancer da AWS, os cookies não estavam sendo enviados de volta pelo navegador.

### Problemas Identificados

1. **Banco de dados inexistente**: O diretório `database/` não existia
2. **Usuários não cadastrados**: O sistema usa arquivos JSON, mas os usuários foram criados no SQLite
3. **Cookies com flag Secure**: Impediam funcionamento via HTTP
4. **Aplicação não estava rodando**: Processo havia parado

## 🛠️ Soluções Aplicadas

### 1. Criação do Banco de Dados
```bash
# Criado diretório database e banco SQLite (não usado pelo sistema)
sudo mkdir -p /opt/assertivia/database
sudo chown assertivia:assertivia /opt/assertivia/database
```

### 2. Criação de Usuários no Sistema JSON
```python
# Criado usuário de teste no sistema JSON correto
from stores.user_store import create_user
user_id = create_user('seu.email@assertivasolucoes.com.br', '123456', 'admin', 'Usuário Teste')
```

### 3. Correção dos Cookies (Principal)
**Arquivo:** `security/cookies.py`

**ANTES:**
```python
def set_cookie(response, name, value, max_age, secure=None):
    if secure is None:
        secure = IS_PRODUCTION  # True em produção
    
    response.set_cookie(
        name, value, max_age=max_age, 
        httponly=True, secure=secure, samesite='Lax'
    )
```

**DEPOIS:**
```python
def set_cookie(response, name, value, max_age, secure=None):
    if secure is None:
        # Temporariamente forçar False para permitir HTTP
        secure = False  # IS_PRODUCTION
    
    response.set_cookie(
        name, value, max_age=max_age, 
        httponly=True, secure=secure, samesite='Lax'
    )
```

### 4. Reinicialização da Aplicação
```bash
# Parar processo anterior
sudo pkill -f 'python.*app.py'

# Iniciar aplicação
cd /opt/assertivia
sudo -u assertivia python3 app.py > app.log 2>&1 &
```

## ✅ Resultado

### Cookies ANTES da correção:
```
Set-Cookie: access_token=...; Secure; HttpOnly; Path=/; SameSite=Lax
Set-Cookie: refresh_token=...; Secure; HttpOnly; Path=/; SameSite=Lax
```

### Cookies DEPOIS da correção:
```
Set-Cookie: access_token=...; HttpOnly; Path=/; SameSite=Lax
Set-Cookie: refresh_token=...; HttpOnly; Path=/; SameSite=Lax
```

## 🎯 Credenciais de Acesso

- **URL:** http://assertivia-alb-9803941.us-east-1.elb.amazonaws.com/
- **Email:** `seu.email@assertivasolucoes.com.br`
- **Senha:** `123456`

## 📚 Outros Usuários Disponíveis

- **Admin:** `admin@assertiva.local` / `admin123`
- **Leandro:** `leandro.albertini@assertivasolucoes.com.br` / (senha existente)

## 🔧 Arquitetura do Sistema

- **Frontend:** Acesso via HTTP através do ALB (Load Balancer)
- **Backend:** Flask rodando na porta 5001 no EC2
- **Autenticação:** JWT tokens armazenados em cookies
- **Usuários:** Armazenados em arquivos JSON (`data/users.json`)
- **Security Group:** Permite acesso à porta 5001 apenas do ALB

## 📝 Lições Aprendidas

1. **Cookies Secure + HTTP = Problema**: Flag `Secure` impede funcionamento via HTTP
2. **Verificar sistema de armazenamento**: Sistema usa JSON, não SQLite
3. **Testar autenticação completa**: Não apenas API, mas fluxo completo com cookies
4. **Monitorar logs**: Verificar se aplicação está rodando corretamente

## 🚀 Status Final

✅ **PROBLEMA RESOLVIDO** - Login funcionando normalmente sem loop infinito.
