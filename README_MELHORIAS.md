# Propostas de melhorias no README e diretrizes para próxima etapa (CSS)

## Objetivo
Este documento concentra sugestões claras e aplicáveis para:
- Corrigir inconsistências e melhorar a legibilidade do README.md
- Deixar o guia mais “executável” para novos usuários e outras IAs
- Preparar a próxima etapa de refinamento visual/UX (CSS)

---

## Principais inconsistências e ajustes propostos

1) Padronização de autenticação (JWT)
- Contexto: O README afirma remoção de decorators antigos e padronização em JWT; porém, ainda cita “session tokens/UUID” e decorators legados (ex.: `@login_required`).
- Ação proposta:
  - Remover referências a “sessões/UUID” e manter apenas “Access/Refresh JWT via cookies httpOnly”.
  - Substituir exemplos de decorators antigos por decorators atuais de JWT (ex.: `@require_auth`, `@require_role`).

2) Hash de senha (Werkzeug vs SHA256)
- Contexto: O README celebra a migração para `generate_password_hash`/`check_password_hash` (Werkzeug), mas, em outra seção, ainda menciona “SHA256”.
- Ação proposta: Remover toda menção a “SHA256” e padronizar para “Werkzeug (PBKDF2-HMAC)”.

3) Porta padrão (5001) x referência a 8080
- Contexto: Execução e acesso usam 5001; Troubleshooting cita 8080.
- Ação proposta: Padronizar todas as referências para 5001 ou, se 8080 for usado em cenários específicos (ex.: proxy/frontend), explicar o motivo.

4) Caracteres com encoding incorreto
- Contexto: Há ocorrências de “�” (indicando problema de encoding) em títulos/texto.
- Ação proposta: Corrigir para UTF-8 e revisar:
  - “### � Adaptador de Autenticação” → “### Adaptador de Autenticação”
  - “**� Sistema Assertiva IA ...**” → corrigir o caractere especial antes do negrito.

5) Limitações e persistência
- Contexto: O README diz “Usuários limitados aos definidos em código” e “dados não persistem entre reinicializações”, mas a pasta `data/` traz `users.json`/`invites.json`.
- Ação proposta: Atualizar para “Persistência local em JSON (adequado para desenvolvimento); para produção, considere DB/serviço gerenciado”.

6) VITE_ORIGIN / CORS
- Contexto: `.env.example` menciona `VITE_ORIGIN`, sugerindo possível frontend separado.
- Ação proposta: Explicar (em README) quando usar `VITE_ORIGIN` e qual origem configurar; se não for mais usado, remover do `.env.example` e do README.

7) Healthcheck (/health)
- Contexto: README descreve `/health` e um JSON de resposta.
- Ação proposta: Confirmar existência da rota. Se não existir, adicionar (ex.: em `routes/api.py`) ou remover a seção.

8) Seções de segurança duplicadas/overlap
- Contexto: “Segurança Avançada” e “Segurança Implementada” cobrem pontos semelhantes.
- Ação proposta: Consolidar em uma única seção objetiva: JWT (access/refresh), cookies httpOnly + SameSite, RBAC, headers de segurança, CSRF.

9) Dependências e versões
- Contexto: Garantir que o `requirements.txt` está coerente com o texto (Flask 2.3.x, openai 1.x, uso de Werkzeug via Flask). Se houver trechos que exigem libs adicionais, documentá-las.
- Ação proposta: Verificar/alinhar versões no README e no `requirements.txt`.

---

## Sugestões de texto (substituições pontuais)

1) Criptografia de senhas
- Antes: “Criptografia: Senhas com hash SHA256”
- Depois: “Criptografia: Senhas com hash via Werkzeug (PBKDF2-HMAC)”

2) Decorators de proteção
- Antes:
```
### Decorators de Proteção
```python
@login_required          # Para páginas HTML
@api_login_required     # Para APIs (retorna JSON)
```
```
- Depois (exemplo genérico, ajustar ao nome real dos decorators atuais):
```
### Autorização baseada em JWT (decorators)
```python
@require_auth            # Autenticação via Access Token (JWT)
@require_role('admin')   # Autorização por perfil (RBAC)
```
```

3) Porta em Troubleshooting
- Antes:
```
1. Porta 8080 ocupada:
   lsof -i :8080
```
- Depois (5001):
```
1. Porta 5001 ocupada:
   lsof -i :5001
```

4) Títulos com “�”
- Antes: “### � Adaptador de Autenticação”
- Depois: “### Adaptador de Autenticação”

5) Limitações (persistência)
- Antes: “Usuários: Limitado aos definidos em código” / “Dados não persistem entre reinicializações”
- Depois: “Persistência local em arquivos JSON (adequada para desenvolvimento). Para produção, recomenda-se banco de dados/serviço gerenciado e migração do auth para provedor (ex.: Cognito).”

6) VITE_ORIGIN
- Inserir no README (se válido): “Se utilizar um frontend separado (ex.: Vite/React), configure `VITE_ORIGIN` no `.env` para habilitar CORS seguro.”

7) Healthcheck (/health)
- Se a rota não existir, sugerir inclusão (exemplo):
```python
@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'sistema_apoio': True,
        'build_version': '1.0.0',
    }), 200
```

---

## Estrutura editorial sugerida (README)

- Adicionar Sumário (TOC) no topo, com âncoras para: Visão Geral, Arquitetura, Como Rodar, Configuração (.env), Acesso, Segurança, IA, Troubleshooting, Deploy, Contribuição.
- Destacar “Execução Rápida” como bloco copiado/colado (one‑liner por etapa).
- Evitar redundâncias entre seções de segurança.
- Manter linguagem consistente (PT-BR), títulos e emojis padronizados.

Exemplo de TOC (modelo):
```
- [Visão Geral](#-visão-geral)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Como Rodar Local](#-como-rodar-local)
- [Configuração Obrigatória (.env)](#-configuração-obrigatória-env)
- [Acesso ao Sistema](#-acesso-ao-sistema)
- [Segurança](#-segurança)
- [Motor de IA](#-motor-de-ia)
- [Troubleshooting](#-troubleshooting)
- [Deploy](#-deploy-de-produção)
- [Contribuição](#-suporte-e-contribuição)
```

---

## Plano de aplicação (passo a passo)

1) Correções imediatas no README
- Corrigir encoding UTF‑8 e os caracteres “�”.
- Padronizar autenticação (remover sessões/UUID; manter JWT access/refresh + cookies httpOnly; decorators atuais).
- Ajustar hash de senhas (Werkzeug PBKDF2‑HMAC).
- Padronizar porta 5001 (ou documentar cenários para 8080).
- Atualizar Limitações e CORS/VITE_ORIGIN.
- Confirmar/implementar `/health` ou remover a seção.

2) Verificações rápidas
- Conferir `requirements.txt` x versões documentadas.
- Conferir existência dos decorators atuais citados no README.

3) Refinos editoriais
- Inserir TOC, uniformizar títulos/emojis, organizar seções de segurança.

4) Próxima etapa (CSS/UX)
- Passar para revisão de `static/css/style.css` (tokens, contraste, foco visível, responsividade, dark mode opcional, componentes-chave).

---

## Checklist de validação

- [ ] README sem caracteres “�” e com UTF‑8 válido
- [ ] Somente JWT documentado (sem “session tokens/UUID”)
- [ ] Hash de senhas: Werkzeug (PBKDF2-HMAC)
- [ ] Porta(s) documentada(s) de forma consistente
- [ ] Limitações/persistência atualizadas (JSON local)
- [ ] VITE_ORIGIN explicado ou removido
- [ ] `/health` existente e retornando 200 (ou seção removida)
- [ ] TOC no topo e seções sem redundância

---

## Preparação para a etapa de CSS (escopo sugerido)

- Tokens de design em `:root` (cores, espaçamentos, radius, sombras, tipografia).
- Contrast ratio AA/AAA para textos e elementos interativos.
- Estados de foco/hover/active consistentes e visíveis (acessibilidade).
- Responsividade: breakpoints claros; grid do atendimento; textarea redimensionável sem “pular” layout.
- Componentes prioritários: navbar, sidebar (collapsed/expanded), botões (primário/secundário/perigo), inputs, alerts/toasts, cartões de resposta.
- Dark Mode (opcional) via `prefers-color-scheme`.

Quando aprovado este documento, aplicaremos as correções no README e seguiremos para a melhoria de CSS/UX.

