#!/usr/bin/env bash
set -e

echo "🚀 Sistema de Gerenciamento de Estoque com MongoDB"
echo "=================================================="

# Navegar para o diretório do script (garante paths relativos corretos)
cd "$(dirname "$0")" || exit 1

# Verificar se MongoDB está rodando
if ! pgrep mongod > /dev/null 2>&1; then
    echo "⚠️  MongoDB não está rodando!"
    echo "💡 Para iniciar o MongoDB: sudo systemctl start mongod"
    printf "\nDeseja tentar iniciar o MongoDB automaticamente? (s/n): "
    read -r resposta

    case "$resposta" in
        [sS])
            echo "🔄 Iniciando MongoDB..."
            if sudo systemctl start mongod; then
                sleep 2
                if pgrep mongod > /dev/null 2>&1; then
                    echo "✅ MongoDB iniciado com sucesso!"
                else
                    echo "❌ Falha ao iniciar MongoDB"
                    exit 1
                fi
            else
                echo "❌ Falha ao executar 'sudo systemctl start mongod' — verifique permissões."
                exit 1
            fi
            ;;
        *)
            echo "❌ MongoDB é necessário para executar o sistema"
            exit 1
            ;;
    esac
else
    echo "✅ MongoDB está rodando"
fi

# Verificar se python3 está disponível
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ python3 não encontrado. Instale o Python 3. Ex.: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Verificar/criar ambiente virtual (venv)
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual em ./venv ..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao criar virtualenv. Verifique permissões e instale python3-venv."
        exit 1
    fi
fi

# Definir paths do venv
VENV_PY="$(pwd)/venv/bin/python"
VENV_PIP="$(pwd)/venv/bin/pip"

# Ativar ambiente virtual (opcional)
echo "🐍 Ativando ambiente virtual..."
# shellcheck disable=SC1091
. venv/bin/activate

# Atualizar pip e instalar dependências se necessário
echo "📦 Verificando dependências..."
$VENV_PY - <<'PYCODE' 2>/dev/null
import sys, importlib
missing=[]
for m in ('pymongo','pandas','openpyxl'):
    try:
        importlib.import_module(m)
    except Exception:
        missing.append(m)
if missing:
    sys.exit(1)
PYCODE

if [ $? -ne 0 ]; then
    echo "❌ Dependências faltando! Instalando via venv..."
    $VENV_PIP install -U pip setuptools wheel || { echo "❌ Falha ao atualizar pip"; exit 1; }
    if [ -f requirements.txt ]; then
        $VENV_PIP install -r requirements.txt || { echo "❌ Falha ao instalar dependências"; exit 1; }
    else
        echo "⚠️ requirements.txt não encontrado — instale as dependências manualmente."
    fi
else
    echo "✅ Dependências OK"
fi

echo ""
echo "🖥️ Iniciando Sistema de Estoque da Adega..."
echo "🚀 Carregando interface gráfica..."
echo ""

# Determinar arquivo principal a executar
if [ -f "main.py" ]; then
    ENTRY="main.py"
elif [ -f "estoque_gui.py" ]; then
    ENTRY="estoque_gui.py"
else
    echo "❌ Nenhum arquivo de entrada encontrado (main.py ou estoque_gui.py). Verifique o projeto."
    exit 1
fi

# Executar aplicação com o python do venv
$VENV_PY "$ENTRY"

echo ""
echo "✅ Sistema finalizado!"