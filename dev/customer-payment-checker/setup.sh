#!/bin/bash

# ===================================================================
# Customer Payment Checker - Setup & Installation Script
# ===================================================================
# 
# Script de configuração automática do ambiente de desenvolvimento
# para o Sistema de Verificação de Pagamentos de Clientes
#
# Autor: Jonatas Pimenta
# Data: 2024-12-28
# Versão: 2.0.0
#
# Uso: ./setup.sh
# ===================================================================

set -e  # Para execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função de log colorido
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Banner do projeto
show_banner() {
    echo -e "${CYAN}"
    echo "====================================================================="
    echo "🏦 Customer Payment Checker - Setup & Installation"
    echo "====================================================================="
    echo "Sistema de Verificação Automática de Pagamentos de Clientes"
    echo "Autor: Jonatas Pimenta | Versão: 2.0.0 | Licença: MIT"
    echo "====================================================================="
    echo -e "${NC}"
}

# Verificar sistema operacional
check_os() {
    log_step "Verificando sistema operacional..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        log_success "Sistema: Linux detectado"
        
        # Detectar distribuição
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$NAME
            VERSION=$VERSION_ID
            log_info "Distribuição: $DISTRO $VERSION"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        log_success "Sistema: macOS detectado"
    else
        OS="Unknown"
        log_warning "Sistema operacional não reconhecido: $OSTYPE"
    fi
}

# Verificar Python
check_python() {
    log_step "Verificando instalação do Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python encontrado: $PYTHON_VERSION"
        
        # Verificar versão mínima (3.8+)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if (( PYTHON_MAJOR >= 3 && PYTHON_MINOR >= 8 )); then
            log_success "Versão do Python é compatível (≥3.8)"
        else
            log_error "Python 3.8+ é necessário. Versão atual: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 não encontrado. Por favor, instale Python 3.8+"
        exit 1
    fi
}

# Verificar Google Chrome
check_chrome() {
    log_step "Verificando instalação do Google Chrome..."
    
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3)
        log_success "Google Chrome encontrado: $CHROME_VERSION"
    elif command -v chromium-browser &> /dev/null; then
        CHROME_VERSION=$(chromium-browser --version | cut -d' ' -f2)
        log_success "Chromium encontrado: $CHROME_VERSION"
    else
        log_warning "Google Chrome não encontrado"
        log_info "Tentando instalar automaticamente..."
        
        if [[ "$OS" == "Linux" ]]; then
            install_chrome_linux
        else
            log_error "Instalação automática não suportada neste SO"
            log_info "Por favor, instale Google Chrome manualmente"
            exit 1
        fi
    fi
}

# Instalar Chrome no Linux
install_chrome_linux() {
    log_step "Instalando Google Chrome no Linux..."
    
    # Baixar e instalar Chrome
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    
    if command -v google-chrome &> /dev/null; then
        log_success "Google Chrome instalado com sucesso"
    else
        log_error "Falha na instalação do Google Chrome"
        exit 1
    fi
}

# Configurar ambiente virtual Python
setup_venv() {
    log_step "Configurando ambiente virtual Python..."
    
    if [ ! -d ".venv" ]; then
        log_info "Criando ambiente virtual..."
        python3 -m venv .venv
        log_success "Ambiente virtual criado"
    else
        log_info "Ambiente virtual já existe"
    fi
    
    # Ativar ambiente virtual
    log_info "Ativando ambiente virtual..."
    source .venv/bin/activate
    log_success "Ambiente virtual ativado"
    
    # Atualizar pip
    log_info "Atualizando pip..."
    pip install --upgrade pip > /dev/null 2>&1
    log_success "Pip atualizado"
}

# Instalar dependências
install_dependencies() {
    log_step "Instalando dependências Python..."
    
    if [ -f "requirements.txt" ]; then
        log_info "Instalando pacotes do requirements.txt..."
        pip install -r requirements.txt > /dev/null 2>&1
        log_success "Dependências instaladas com sucesso"
    else
        log_error "Arquivo requirements.txt não encontrado"
        exit 1
    fi
}

# Verificar instalação
verify_installation() {
    log_step "Verificando instalação..."
    
    # Verificar se os pacotes foram instalados
    python3 -c "import openpyxl, selenium, webdriver_manager" 2>/dev/null
    if [ $? -eq 0 ]; then
        log_success "Todos os pacotes Python estão instalados"
    else
        log_error "Alguns pacotes Python estão faltando"
        exit 1
    fi
    
    # Verificar scripts executáveis
    if [ -x "executar.sh" ] && [ -x "teste_rapido.sh" ]; then
        log_success "Scripts de execução estão prontos"
    else
        log_info "Tornando scripts executáveis..."
        chmod +x executar.sh teste_rapido.sh
        log_success "Permissões de execução configuradas"
    fi
}

# Criar planilha de exemplo
create_example_data() {
    log_step "Criando dados de exemplo..."
    
    if [ ! -f "dados_clientes.xlsx" ]; then
        log_info "Gerando planilha de exemplo..."
        python3 criar_planilha_exemplo.py > /dev/null 2>&1
        
        if [ -f "dados_clientes_exemplo.xlsx" ]; then
            cp dados_clientes_exemplo.xlsx dados_clientes.xlsx
            log_success "Planilha de exemplo criada"
        else
            log_warning "Não foi possível criar planilha de exemplo"
        fi
    else
        log_info "Planilha de dados já existe"
    fi
}

# Executar teste de validação
run_validation_test() {
    log_step "Executando teste de validação..."
    
    read -p "Deseja executar o teste automático agora? (s/n): " run_test
    
    if [[ $run_test =~ ^[Ss]$ ]]; then
        log_info "Iniciando teste rápido..."
        echo
        ./teste_rapido.sh
        echo
        log_success "Teste de validação concluído"
    else
        log_info "Teste pulado. Execute './teste_rapido.sh' quando desejar"
    fi
}

# Mostrar informações finais
show_final_info() {
    echo
    echo -e "${GREEN}====================================================================="
    echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "====================================================================="
    echo -e "${NC}"
    echo -e "${CYAN}📋 Informações do Sistema:${NC}"
    echo "   🖥️  Sistema Operacional: $OS"
    echo "   🐍 Python: $PYTHON_VERSION"
    echo "   🌐 Navegador: Google Chrome $CHROME_VERSION"
    echo "   📦 Ambiente Virtual: .venv (ativado)"
    echo
    echo -e "${CYAN}🚀 Como usar:${NC}"
    echo "   ./executar.sh        # Interface completa"
    echo "   ./teste_rapido.sh    # Teste rápido (3 clientes)"
    echo
    echo -e "${CYAN}📚 Documentação:${NC}"
    echo "   README.md                 # Visão geral do projeto"
    echo "   MANUAL_USO.md            # Manual detalhado"
    echo "   DOCUMENTACAO_TECNICA.md  # Documentação técnica"
    echo "   CHANGELOG.md             # Histórico de mudanças"
    echo
    echo -e "${CYAN}📞 Suporte:${NC}"
    echo "   Em caso de problemas, consulte a documentação ou"
    echo "   verifique os logs de erro para diagnóstico."
    echo
    echo -e "${GREEN}====================================================================="
    echo "Pronto para uso! 🎯"
    echo "====================================================================="
    echo -e "${NC}"
}

# Função principal
main() {
    show_banner
    
    log_info "Iniciando configuração do ambiente..."
    echo
    
    # Verificações do sistema
    check_os
    check_python
    check_chrome
    echo
    
    # Configuração do ambiente
    setup_venv
    install_dependencies
    echo
    
    # Validação e preparação
    verify_installation
    create_example_data
    echo
    
    # Teste opcional
    run_validation_test
    
    # Informações finais
    show_final_info
}

# Executar se for chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
