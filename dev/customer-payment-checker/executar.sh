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
        /home/lion/Documentos/Projetos/jonatas-portfolio/dev/customer-payment-checker/.venv/bin/python criar_planilha_exemplo.py
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
echo "1. 🧪 TESTE RÁPIDO - Apenas 3 clientes (recomendado para primeira vez)"
echo "2. 🎯 EXECUÇÃO COMPLETA - Você escolhe quantos clientes processar"
echo "3. ❌ Cancelar"
echo ""
read -p "Escolha uma opção (1-3): " modo

case $modo in
    1)
        echo ""
        echo "🧪 TESTE RÁPIDO INICIADO"
        echo "========================"
        echo "✅ Processará apenas os primeiros 3 clientes"
        echo "⚠️  IMPORTANTE: Não feche o navegador manualmente!"
        echo ""
        read -p "Pressione Enter para continuar..."
        
        # Executar com opções predefinidas para teste
        echo "2" > /tmp/opcoes_teste.txt
        echo "3" >> /tmp/opcoes_teste.txt
        /home/lion/Documentos/Projetos/jonatas-portfolio/dev/customer-payment-checker/.venv/bin/python verificador_pagamentos.py < /tmp/opcoes_teste.txt
        rm -f /tmp/opcoes_teste.txt
        ;;
    2)
        echo ""
        echo "🎯 EXECUÇÃO COMPLETA"
        echo "===================="
        echo "✅ Você poderá escolher quantos clientes processar"
        echo "⚠️  IMPORTANTE: Não feche o navegador manualmente!"
        echo ""
        read -p "Pressione Enter para continuar..."
        
        # Executar normalmente
        /home/lion/Documentos/Projetos/jonatas-portfolio/dev/customer-payment-checker/.venv/bin/python verificador_pagamentos.py
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
