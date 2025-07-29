#!/bin/bash

echo "🧪 TESTE RÁPIDO - Verificador de Pagamentos"
echo "==========================================="
echo ""
echo "Este script vai testar o sistema com apenas 3 clientes da planilha de exemplo."
echo ""

# Criar planilha de exemplo se não existir
if [ ! -f "dados_clientes.xlsx" ]; then
    echo "📝 Criando planilha de exemplo para teste..."
    /home/lion/Documentos/Projetos/jonatas-portfolio/dev/customer-payment-checker/.venv/bin/python criar_planilha_exemplo.py
    mv dados_clientes_exemplo.xlsx dados_clientes.xlsx
    echo "✅ Planilha de teste preparada!"
fi

# Deletar planilha de fechamento anterior se existir
if [ -f "planilha_fechamento.xlsx" ]; then
    rm planilha_fechamento.xlsx
    echo "🗑️  Limpando resultados anteriores..."
fi

echo ""
echo "🚀 Iniciando teste com os primeiros 3 clientes..."
echo "⚠️  O programa vai automaticamente processar apenas 3 clientes para teste."
echo "⚠️  IMPORTANTE: Não feche o navegador manualmente!"
echo ""
echo "Pressione Enter para continuar ou Ctrl+C para cancelar..."
read

# Criar arquivo temporário com opções para teste automático
echo "2" > /tmp/opcoes_teste.txt
echo "3" >> /tmp/opcoes_teste.txt

# Executar o script principal com as opções predefinidas
/home/lion/Documentos/Projetos/jonatas-portfolio/dev/customer-payment-checker/.venv/bin/python verificador_pagamentos.py < /tmp/opcoes_teste.txt

# Limpar arquivo temporário
rm -f /tmp/opcoes_teste.txt

echo ""
echo "✅ Teste concluído!"
echo "📊 Verifique o arquivo 'planilha_fechamento.xlsx' para ver os resultados."
echo ""
echo "💡 Para usar com sua planilha real:"
echo "   1. Substitua 'dados_clientes.xlsx' pela sua planilha"
echo "   2. Execute: ./executar.sh"
echo "   3. Escolha quantos clientes processar"
