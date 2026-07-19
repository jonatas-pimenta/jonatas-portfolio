#!/usr/bin/env bash
set -e

echo "🚀 STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM"
echo "=================================================="

# Navegar para o diretório do script (garante paths relativos corretos)
cd "$(dirname "$0")" || exit 1

# Verificar se python3 está disponível
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ python3 não encontrado. Instale o Python 3. Ex.: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Verificar ambiente virtual .venv e criar/recriar se necessário.
if [ ! -d ".venv" ] || [ ! -x ".venv/bin/python" ]; then
    echo "🐍 Ambiente .venv não encontrado ou inválido. Criando em ./.venv ..."
    python3 -m venv .venv || {
        echo "❌ Falha ao criar virtualenv. Verifique permissões e instale python3-venv."
        exit 1
    }
fi

VENV_DIR=".venv"

# Definir path do python do venv
VENV_PY="$(pwd)/$VENV_DIR/bin/python"

# Não depende de "activate": usa o Python absoluto do venv selecionado.
echo "🐍 Usando ambiente virtual: $VENV_DIR"

# Atualizar pip e instalar dependências se necessário
echo "📦 Verificando dependências..."
if ! "$VENV_PY" - <<'PYCODE' 2>/dev/null
import sys, importlib
missing=[]
for m in ('pandas','openpyxl','bcrypt'):
    try:
        importlib.import_module(m)
    except Exception:
        missing.append(m)
if missing:
    sys.exit(1)
PYCODE
then
    echo "❌ Dependências faltando! Instalando via venv..."
    "$VENV_PY" -m pip install -U pip setuptools wheel || { echo "❌ Falha ao atualizar pip"; exit 1; }
    if [ -f requirements.txt ]; then
        "$VENV_PY" -m pip install -r requirements.txt || { echo "❌ Falha ao instalar dependências"; exit 1; }
    else
        echo "⚠️ requirements.txt não encontrado — instale as dependências manualmente."
    fi
else
    echo "✅ Dependências OK"
fi

echo ""
echo "🖥️ Iniciando Sistema STOCKFLOW - FLUXO DE ESTOQUE COM CRIPTOGRAFIA E BACKUP EM NUVEM..."
echo "🚀 Carregando interface gráfica..."
echo ""

# Determinar modulo principal a executar
if [ -f "frontend/gui.py" ]; then
    ENTRY_MODULE="frontend.gui"
else
    echo "❌ Arquivo de entrada nao encontrado (frontend/gui.py). Verifique o projeto."
    exit 1
fi

# Executar aplicacao como modulo para manter imports de pacote (backend/frontend)
"$VENV_PY" -m "$ENTRY_MODULE"

echo ""
echo "✅ Sistema finalizado!"