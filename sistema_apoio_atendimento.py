#!/usr/bin/env python3
"""
Sistema de Apoio ao Atendimento Assertiva
Copia e cola: pergunta do cliente → resposta pronta para atendimento
"""

import os
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

class SistemaApoioAtendimento:
    def __init__(self):
        """Inicializa o sistema de apoio"""
        # Configurar OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY não encontrada no arquivo .env")
        
        self.client = OpenAI(api_key=api_key.strip())
        
        # Carregar conhecimento dos guias práticos
        self.conhecimento = self.carregar_guias_praticos()
        
        print("✅ Sistema de Apoio ao Atendimento inicializado")
        print(f"📚 {len(self.conhecimento)} guias práticos carregados")
        print("🎯 Pronto para gerar respostas de atendimento!\n")
    
    def carregar_guias_praticos(self):
        """Carrega todos os guias práticos"""
        pasta_guias = Path("GUIAS_PRATICOS_ASSERTIVA")
        conhecimento = {}
        
        if not pasta_guias.exists():
            print("⚠️  Pasta de guias práticos não encontrada")
            return {}
        
        for arquivo in pasta_guias.glob("*.md"):
            if arquivo.name.startswith("00_"):  # Pular índice
                continue
                
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Nome limpo do guia
            nome_limpo = arquivo.stem.replace("_guia_pratico", "").replace("_", " ")
            conhecimento[nome_limpo] = conteudo
        
        return conhecimento
    
    def buscar_informacao_relevante(self, pergunta_cliente):
        """Busca informações relevantes nos guias práticos"""
        pergunta_lower = pergunta_cliente.lower()
        informacoes_relevantes = []
        
        # Palavras-chave para busca
        palavras_chave = pergunta_lower.split()
        
        for titulo, conteudo in self.conhecimento.items():
            conteudo_lower = conteudo.lower()
            relevancia = 0
            
            # Calcular relevância
            for palavra in palavras_chave:
                if len(palavra) > 3:  # Ignorar palavras muito pequenas
                    relevancia += conteudo_lower.count(palavra)
            
            if relevancia > 0:
                informacoes_relevantes.append((titulo, conteudo, relevancia))
        
        # Ordenar por relevância e retornar as 2 mais relevantes
        informacoes_relevantes.sort(key=lambda x: x[2], reverse=True)
        return informacoes_relevantes[:2]
    
    def gerar_resposta_atendimento(self, pergunta_cliente):
        """Gera resposta completa de atendimento"""
        print(f"🔍 [APOIO] Iniciando geração de resposta para: '{pergunta_cliente}'")

        # Buscar informações relevantes
        print("📚 [APOIO] Buscando informações relevantes...")
        info_relevantes = self.buscar_informacao_relevante(pergunta_cliente)
        print(f"📋 [APOIO] Encontradas {len(info_relevantes)} informações relevantes")
        
        if not info_relevantes:
            return "❌ Não encontrei informações específicas sobre essa pergunta nos guias. Recomendo consultar a documentação completa ou escalar para um especialista."
        
        # Construir contexto
        contexto = "GUIAS PRÁTICOS DA PLATAFORMA ASSERTIVA:\n\n"
        
        for titulo, conteudo, relevancia in info_relevantes:
            contexto += f"=== {titulo.upper()} ===\n"
            # Pegar apenas partes relevantes para não exceder limite
            contexto += conteudo[:2000] + "\n\n"
        
        # Prompt especializado para atendimento
        prompt = f"""Você é um especialista em atendimento ao cliente da plataforma Assertiva.

INSTRUÇÕES OBRIGATÓRIAS:
- Responda como um atendente experiente e cordial
- Use APENAS as informações dos guias práticos fornecidos
- Formate a resposta como uma conversa telefônica real
- Inclua passos numerados e descrições visuais específicas
- Use linguagem clara e profissional
- Seja específico sobre localização de elementos (botões, menus, etc.)
- Inclua valores e exemplos quando disponíveis nos guias
- IMPORTANTE: Se a resposta envolver ações que requerem acesso de administrador, adicione no final da mensagem: "*Observação*: Essa ação só pode ser realizada com acesso de administrador"

FORMATO DA RESPOSTA:
📞 **Atendimento Assertiva**

**Cliente:** [repita a pergunta]

**Atendente:** "Olá! [resposta completa com orientação passo a passo]"

GUIAS DISPONÍVEIS:
{contexto}

PERGUNTA DO CLIENTE:
{pergunta_cliente}

RESPOSTA DE ATENDIMENTO:"""

        try:
            print("🤖 [APOIO] Enviando requisição para OpenAI...")
            resposta = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em atendimento ao cliente da Assertiva. Sempre responda como se fosse uma conversa telefônica real, com passos específicos e descrições visuais detalhadas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.3
            )

            print("✅ [APOIO] Resposta recebida da OpenAI com sucesso!")
            resposta_texto = resposta.choices[0].message.content
            print(f"📝 [APOIO] Tamanho da resposta: {len(resposta_texto)} caracteres")
            return resposta_texto

        except Exception as e:
            print(f"💥 [APOIO] ERRO na OpenAI: {str(e)}")
            import traceback
            print(f"📋 [APOIO] Traceback: {traceback.format_exc()}")
            return f"❌ Erro ao processar pergunta: {e}"

def main():
    """Interface principal do sistema"""
    print("🎯 === SISTEMA DE APOIO AO ATENDIMENTO ASSERTIVA ===\n")
    
    try:
        # Inicializar sistema
        sistema = SistemaApoioAtendimento()
        
        print("💬 COMO USAR:")
        print("1. Cole a pergunta do cliente")
        print("2. Pressione Enter")
        print("3. Copie a resposta gerada")
        print("4. Cole na conversa com o cliente")
        print("\nDigite 'sair' para encerrar\n")
        print("="*60)
        
        while True:
            print("\n📝 PERGUNTA DO CLIENTE:")
            pergunta = input(">>> ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Sistema encerrado!")
                break
            
            if not pergunta:
                print("⚠️  Digite uma pergunta válida")
                continue
            
            print("\n🔄 Gerando resposta...")
            resposta = sistema.gerar_resposta_atendimento(pergunta)
            
            print("\n" + "="*60)
            print("📋 RESPOSTA PARA COPIAR E COLAR:")
            print("="*60)
            print(resposta)
            print("="*60)
            print("✅ Resposta pronta! Copie e cole na conversa com o cliente.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
