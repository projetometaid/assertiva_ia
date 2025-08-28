#!/bin/bash

echo "🚀 === SISTEMA LOCAL SIMPLES ==="
echo "📋 Instalando dependências..."

# Instalar dependências
pip install -r requirements.txt

echo "🔧 Iniciando servidor local..."
echo "🌐 Acesse: http://localhost:8080"
echo "⏹️  Para parar: Ctrl+C"

# Rodar aplicação
python app_simples.py
