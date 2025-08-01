#!/bin/bash

clear
echo "🚀 VERIFICADOR DE PAGAMENTOS DE CLIENTES"
echo "========================================"
echo ""
echo "📋 Este programa verifica o status de pagamento dos seus clientes"
echo "   consultando CPFs em: https://consultcpf-devaprender.netlify.app"
echo ""

# Verificar se a planilha de dados existe
if [ ! -f "dados_clientes.xlsx" ]; then
    echo "❌ Planilha 'dados_clientes.xlsx' não encontrada!"
    echo ""
    echo "🎯 Opções disponíveis:"
    echo "1. Criar planilha de exemplo para teste"
    echo "2. Sair (adicione sua planilha e execute novamente)"
    echo ""
    read -p "Escolha uma opção (1-2): " opcao
    
    if [ "$opcao" = "1" ]; then
        echo ""
        echo "📝 Criando planilha de exemplo..."
        .venv/bin/python -c "
import sys
sys.path.append('.')
from verificador_pagamentos import criar_planilha_exemplo
criar_planilha_exemplo()
"
        mv dados_clientes_exemplo.xlsx dados_clientes.xlsx
        echo "✅ Planilha de exemplo criada como 'dados_clientes.xlsx'"
        echo ""
    else
        echo "❌ Processo cancelado."
        echo "💡 Adicione sua planilha como 'dados_clientes.xlsx' e execute novamente."
        exit 1
    fi
fi

echo "🎛️  MODO DE EXECUÇÃO:"
echo "1. 📊 ESCOLHER QUANTIDADE - Defina quantos clientes processar (recomendado para teste)"
echo "2. 🎯 PROCESSAR TODOS - Todos os clientes da planilha"
echo "3. ❌ Cancelar"
echo ""
read -p "Escolha uma opção (1-3): " modo

case $modo in
    1)
        echo ""
        echo "📊 PROCESSAMENTO PERSONALIZADO"
        echo "=============================="
        echo "💡 Para teste rápido, recomendamos 3-5 clientes"
        echo ""
        read -p "Quantos clientes você quer processar? " quantidade
        
        if [[ "$quantidade" =~ ^[0-9]+$ ]] && [ "$quantidade" -gt 0 ]; then
            echo ""
            echo "✅ Processará os primeiros $quantidade clientes"
            echo "⚠️  IMPORTANTE: Não feche o navegador manualmente!"
            echo ""
            read -p "Pressione Enter para continuar..."
            
            # Executar com quantidade específica
            echo "2" > /tmp/opcoes_processamento.txt
            echo "$quantidade" >> /tmp/opcoes_processamento.txt
            .venv/bin/python verificador_pagamentos.py < /tmp/opcoes_processamento.txt
            rm -f /tmp/opcoes_processamento.txt
        else
            echo "❌ Quantidade inválida. Digite apenas números maiores que 0."
            exit 1
        fi
        ;;
    2)
        echo ""
        echo "🎯 PROCESSAMENTO COMPLETO"
        echo "========================="
        echo "✅ Processará TODOS os clientes da planilha"
        echo "⚠️  IMPORTANTE: Não feche o navegador manualmente!"
        echo ""
        read -p "Pressione Enter para continuar..."
        
        # Executar processando todos
        echo "1" > /tmp/opcoes_processamento.txt
        .venv/bin/python verificador_pagamentos.py < /tmp/opcoes_processamento.txt
        rm -f /tmp/opcoes_processamento.txt
        ;;
    3)
        echo "❌ Processo cancelado pelo usuário."
        exit 0
        ;;
    *)
        echo "❌ Opção inválida. Execute novamente."
        exit 1
        ;;
esac

echo ""
echo "✅ PROCESSO FINALIZADO!"
echo "======================"
echo "📊 Verifique o arquivo 'planilha_fechamento.xlsx' para ver os resultados."
echo ""
echo "💡 Estrutura do arquivo de saída:"
echo "   - Nome, Valor, CPF, Vencimento, Status"
echo "   - Data do Pagamento (se em dia)"
echo "   - Método de Pagamento (se em dia)"
echo ""
echo "🔄 Para processar mais clientes, execute novamente: ./executar.sh"
