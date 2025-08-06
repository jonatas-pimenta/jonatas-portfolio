#!/bin/bash

# Cores para melhor visualização
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Função para exibir cabeçalho
show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                🚀 CUSTOMER PAYMENT CHECKER                  ║${NC}"
    echo -e "${CYAN}║              Sistema de Verificação de Pagamentos           ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}📋 Automatiza verificação de status de pagamentos via web scraping${NC}"
    echo -e "${WHITE}🌐 Site: https://consultcpf-devaprender.netlify.app${NC}"
    echo ""
}

# Função para verificar dependências
check_dependencies() {
    echo -e "${YELLOW}🔍 Verificando dependências do sistema...${NC}"
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 não encontrado. Instale o Python 3.8+${NC}"
        exit 1
    fi
    
    # Verificar Google Chrome
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
        echo -e "${RED}❌ Google Chrome não encontrado. Instale o Google Chrome${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependências do sistema OK${NC}"
}

# Função para verificar planilha de entrada
check_input_file() {
    if [ ! -f "dados_clientes.xlsx" ]; then
        echo -e "${RED}❌ Planilha 'dados_clientes.xlsx' não encontrada!${NC}"
        echo ""
        echo -e "${YELLOW}💡 Para usar este sistema, você precisa de uma planilha Excel com:${NC}"
        echo -e "${WHITE}   • Coluna A: Nome do cliente${NC}"
        echo -e "${WHITE}   • Coluna B: Valor (ex: 1500.00)${NC}"
        echo -e "${WHITE}   • Coluna C: CPF (apenas números: 12345678901)${NC}"
        echo -e "${WHITE}   • Coluna D: Data de vencimento (ex: 2024-01-15)${NC}"
        echo ""
        echo -e "${CYAN}📁 Salve sua planilha como 'dados_clientes.xlsx' neste diretório${NC}"
        echo -e "${CYAN}   e execute novamente: ./executar.sh${NC}"
        echo ""
        exit 1
    fi
    echo -e "${GREEN}✅ Planilha de entrada encontrada${NC}"
}

# Função para configurar ambiente virtual
setup_virtual_env() {
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}⚙️  Configurando ambiente virtual pela primeira vez...${NC}"
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install selenium openpyxl webdriver-manager
        echo -e "${GREEN}✅ Ambiente virtual configurado com sucesso!${NC}"
        echo ""
    else
        echo -e "${GREEN}✅ Ambiente virtual já configurado${NC}"
    fi
    
    # Ativar ambiente virtual
    source .venv/bin/activate
}

# Função para mostrar prévia dos clientes
show_preview() {
    echo -e "${CYAN}📊 Carregando prévia dos clientes...${NC}"
    python3 -c "
import openpyxl
import sys

try:
    wb = openpyxl.load_workbook('dados_clientes.xlsx')
    ws = wb['Sheet1']
    
    print('\\n📋 Prévia dos clientes na planilha:')
    print('-' * 60)
    
    count = 0
    total = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is not None:
            total += 1
            if count < 10:
                nome, valor, cpf, vencimento = row
                print(f'{count+1:2d}. {nome} (CPF: {cpf}) - R$ {valor}')
                count += 1
    
    if total > 10:
        print(f'    ... e mais {total - 10} clientes')
    
    print(f'\\n📊 Total de clientes na planilha: {total}')
    print(f'total_clientes={total}')
    
except Exception as e:
    print(f'❌ Erro ao ler planilha: {e}')
    sys.exit(1)
" | tee /tmp/preview_output.txt

    # Extrair total de clientes
    TOTAL_CLIENTES=$(grep "total_clientes=" /tmp/preview_output.txt | cut -d'=' -f2)
    rm -f /tmp/preview_output.txt
    
    if [ -z "$TOTAL_CLIENTES" ] || [ "$TOTAL_CLIENTES" -eq 0 ]; then
        echo -e "${RED}❌ Nenhum cliente encontrado na planilha${NC}"
        exit 1
    fi
}

# Função para menu principal
show_main_menu() {
    echo ""
    echo -e "${PURPLE}🎛️  CONTROLES DE PROCESSAMENTO:${NC}"
    echo -e "${WHITE}1. 📊 PROCESSAR TODOS - Todos os $TOTAL_CLIENTES clientes${NC}"
    echo -e "${WHITE}2. 🎯 PROCESSAMENTO LIMITADO - Primeiros N clientes${NC}"
    echo -e "${WHITE}3. 📦 PROCESSAMENTO EM LOTES - Grupos com pausas${NC}"
    echo -e "${WHITE}4. 📐 INTERVALO ESPECÍFICO - Do cliente X ao Y${NC}"
    echo -e "${WHITE}5. 🔄 CONTINUAÇÃO - Retomar execução interrompida${NC}"
    echo -e "${WHITE}6. ❌ Cancelar${NC}"
    echo ""
}

# Função para validar número
validate_number() {
    local input=$1
    local min=$2
    local max=$3
    
    if [[ ! "$input" =~ ^[0-9]+$ ]]; then
        return 1
    fi
    
    if [ "$input" -lt "$min" ] || [ "$input" -gt "$max" ]; then
        return 1
    fi
    
    return 0
}

# Função para processar opção 1 - Todos os clientes
process_all_clients() {
    echo ""
    echo -e "${GREEN}🎯 PROCESSAMENTO COMPLETO${NC}"
    echo -e "${GREEN}=========================${NC}"
    echo -e "${WHITE}✅ Processará TODOS os $TOTAL_CLIENTES clientes da planilha${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANTE: Não feche o navegador manualmente!${NC}"
    echo -e "${YELLOW}⚠️  AVISO: Este processo pode demorar bastante${NC}"
    echo ""
    read -p "Pressione Enter para continuar ou Ctrl+C para cancelar..."
    
    # Criar arquivo de opções temporário
    echo "1" > /tmp/opcoes_processamento.txt
    execute_python_script
}

# Função para processar opção 2 - Primeiros N clientes
process_limited_clients() {
    echo ""
    echo -e "${BLUE}📊 PROCESSAMENTO LIMITADO${NC}"
    echo -e "${BLUE}==========================${NC}"
    echo -e "${YELLOW}💡 Para teste rápido, recomendamos 3-5 clientes${NC}"
    echo ""
    
    while true; do
        read -p "Quantos clientes você quer processar? (1-$TOTAL_CLIENTES): " quantidade
        
        if validate_number "$quantidade" 1 "$TOTAL_CLIENTES"; then
            echo ""
            echo -e "${GREEN}✅ Processará os primeiros $quantidade clientes${NC}"
            echo -e "${YELLOW}⚠️  IMPORTANTE: Não feche o navegador manualmente!${NC}"
            echo ""
            read -p "Pressione Enter para continuar..."
            
            # Criar arquivo de opções temporário
            echo "2" > /tmp/opcoes_processamento.txt
            echo "$quantidade" >> /tmp/opcoes_processamento.txt
            execute_python_script
            break
        else
            echo -e "${RED}❌ Digite um número entre 1 e $TOTAL_CLIENTES${NC}"
        fi
    done
}

# Função para processar opção 3 - Lotes com pausas
process_batch_clients() {
    echo ""
    echo -e "${PURPLE}📦 PROCESSAMENTO EM LOTES${NC}"
    echo -e "${PURPLE}===========================${NC}"
    echo -e "${WHITE}💡 Processa grupos de clientes com pausas configuráveis${NC}"
    echo ""
    
    while true; do
        read -p "Tamanho de cada lote (1-$TOTAL_CLIENTES): " tamanho_lote
        
        if validate_number "$tamanho_lote" 1 "$TOTAL_CLIENTES"; then
            total_lotes=$(( (TOTAL_CLIENTES + tamanho_lote - 1) / tamanho_lote ))
            echo ""
            echo -e "${GREEN}✅ Configuração do lote:${NC}"
            echo -e "${WHITE}   • Tamanho por lote: $tamanho_lote clientes${NC}"
            echo -e "${WHITE}   • Total de lotes: $total_lotes${NC}"
            echo -e "${WHITE}   • Total de clientes: $TOTAL_CLIENTES${NC}"
            echo -e "${YELLOW}⚠️  Haverá pausa entre cada lote para confirmação${NC}"
            echo ""
            read -p "Pressione Enter para continuar..."
            
            # Criar arquivo de opções temporário
            echo "3" > /tmp/opcoes_processamento.txt
            echo "$tamanho_lote" >> /tmp/opcoes_processamento.txt
            execute_python_script
            break
        else
            echo -e "${RED}❌ Digite um número entre 1 e $TOTAL_CLIENTES${NC}"
        fi
    done
}

# Função para processar opção 4 - Intervalo específico
process_range_clients() {
    echo ""
    echo -e "${CYAN}📐 INTERVALO ESPECÍFICO${NC}"
    echo -e "${CYAN}=======================${NC}"
    echo -e "${WHITE}💡 Processa clientes de uma posição específica até outra${NC}"
    echo ""
    
    while true; do
        read -p "Começar do cliente número (1-$TOTAL_CLIENTES): " inicio
        
        if validate_number "$inicio" 1 "$TOTAL_CLIENTES"; then
            while true; do
                read -p "Terminar no cliente número ($inicio-$TOTAL_CLIENTES): " fim
                
                if validate_number "$fim" "$inicio" "$TOTAL_CLIENTES"; then
                    quantidade_intervalo=$((fim - inicio + 1))
                    echo ""
                    echo -e "${GREEN}✅ Configuração do intervalo:${NC}"
                    echo -e "${WHITE}   • Do cliente $inicio ao $fim${NC}"
                    echo -e "${WHITE}   • Total a processar: $quantidade_intervalo clientes${NC}"
                    echo ""
                    read -p "Pressione Enter para continuar..."
                    
                    # Criar arquivo de opções temporário
                    echo "4" > /tmp/opcoes_processamento.txt
                    echo "$inicio" >> /tmp/opcoes_processamento.txt
                    echo "$fim" >> /tmp/opcoes_processamento.txt
                    execute_python_script
                    return
                else
                    echo -e "${RED}❌ Digite um número entre $inicio e $TOTAL_CLIENTES${NC}"
                fi
            done
        else
            echo -e "${RED}❌ Digite um número entre 1 e $TOTAL_CLIENTES${NC}"
        fi
    done
}

# Função para processar opção 5 - Continuação
process_continue_clients() {
    echo ""
    echo -e "${YELLOW}🔄 CONTINUAÇÃO DE EXECUÇÃO${NC}"
    echo -e "${YELLOW}==========================${NC}"
    echo -e "${WHITE}💡 Retoma processamento a partir de uma posição específica${NC}"
    echo ""
    
    while true; do
        read -p "Continuar a partir do cliente número (1-$TOTAL_CLIENTES): " inicio
        
        if validate_number "$inicio" 1 "$TOTAL_CLIENTES"; then
            restantes=$((TOTAL_CLIENTES - inicio + 1))
            echo ""
            echo -e "${GREEN}✅ Configuração de continuação:${NC}"
            echo -e "${WHITE}   • Continuar do cliente $inicio até o final${NC}"
            echo -e "${WHITE}   • Clientes restantes: $restantes${NC}"
            echo ""
            read -p "Pressione Enter para continuar..."
            
            # Criar arquivo de opções temporário
            echo "5" > /tmp/opcoes_processamento.txt
            echo "$inicio" >> /tmp/opcoes_processamento.txt
            execute_python_script
            break
        else
            echo -e "${RED}❌ Digite um número entre 1 e $TOTAL_CLIENTES${NC}"
        fi
    done
}

# Função para executar o script Python
execute_python_script() {
    echo ""
    echo -e "${GREEN}🚀 INICIANDO PROCESSAMENTO...${NC}"
    echo -e "${GREEN}==============================${NC}"
    echo ""
    
    # Mostrar recursos avançados ativados
    echo -e "${PURPLE}🛡️  RECURSOS AVANÇADOS ATIVADOS:${NC}"
    echo -e "${WHITE}   ✅ Rate Limiting - Proteção anti-bloqueio${NC}"
    echo -e "${WHITE}   ✅ Sistema de Recovery - Tolerância a falhas${NC}"
    echo -e "${WHITE}   ✅ Validação de Dados - Verificação de CPF${NC}"
    echo -e "${WHITE}   ✅ Interface Progressiva - Feedback em tempo real${NC}"
    echo -e "${WHITE}   ✅ Logs Detalhados - Rastreamento completo${NC}"
    echo -e "${WHITE}   ✅ Formatação Automática - CPF e valores${NC}"
    echo ""
    
    # Executar Python script
    if python verificador_pagamentos.py < /tmp/opcoes_processamento.txt; then
        show_success_message
    else
        show_error_message
    fi
    
    # Limpar arquivo temporário
    rm -f /tmp/opcoes_processamento.txt
}

# Função para mostrar mensagem de sucesso
show_success_message() {
    echo ""
    echo -e "${GREEN}✅ PROCESSO FINALIZADO COM SUCESSO!${NC}"
    echo -e "${GREEN}====================================${NC}"
    echo -e "${WHITE}📊 Arquivo gerado: planilha_fechamento.xlsx${NC}"
    echo ""
    echo -e "${CYAN}💡 Estrutura do arquivo de saída:${NC}"
    echo -e "${WHITE}   • Nome, Valor, CPF, Vencimento, Status${NC}"
    echo -e "${WHITE}   • Data do Pagamento (se em dia)${NC}"
    echo -e "${WHITE}   • Método de Pagamento (se em dia)${NC}"
    echo ""
    echo -e "${YELLOW}🔄 Para processar mais clientes, execute: ./executar.sh${NC}"
    echo ""
}

# Função para mostrar mensagem de erro
show_error_message() {
    echo ""
    echo -e "${RED}❌ ERRO DURANTE O PROCESSAMENTO${NC}"
    echo -e "${RED}===============================${NC}"
    echo -e "${WHITE}Verifique os logs acima para mais detalhes${NC}"
    echo ""
    echo -e "${YELLOW}💡 Possíveis soluções:${NC}"
    echo -e "${WHITE}   • Verificar conexão com a internet${NC}"
    echo -e "${WHITE}   • Verificar se o Google Chrome está instalado${NC}"
    echo -e "${WHITE}   • Verificar formato da planilha dados_clientes.xlsx${NC}"
    echo -e "${WHITE}   • Tentar novamente com menos clientes${NC}"
    echo ""
}

# Função principal
main() {
    show_header
    check_dependencies
    check_input_file
    setup_virtual_env
    show_preview
    
    while true; do
        show_main_menu
        read -p "Escolha uma opção (1-6): " opcao
        
        case $opcao in
            1)
                process_all_clients
                break
                ;;
            2)
                process_limited_clients
                break
                ;;
            3)
                process_batch_clients
                break
                ;;
            4)
                process_range_clients
                break
                ;;
            5)
                process_continue_clients
                break
                ;;
            6)
                echo ""
                echo -e "${YELLOW}❌ Processo cancelado pelo usuário.${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo ""
                echo -e "${RED}❌ Opção inválida. Digite um número de 1 a 6.${NC}"
                sleep 2
                show_header
                echo -e "${GREEN}✅ Planilha de entrada encontrada${NC}"
                echo -e "${GREEN}✅ Ambiente virtual já configurado${NC}"
                echo -e "${GREEN}✅ Total de clientes: $TOTAL_CLIENTES${NC}"
                ;;
        esac
    done
}

# Executar função principal
main