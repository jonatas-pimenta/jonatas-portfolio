# 📖 Guia de Uso - Customer Payment Checker

## 🚀 Início Rápido

### 1️⃣ **Execução Principal**
```bash
./executar.sh
```
*Interface completa com todas as opções de processamento*

### 2️⃣ **Teste Rápido**
```bash
./teste_rapido.sh
```
*Execução automática com 3 clientes para validação*

---

## 📋 Preparação dos Dados

### 📊 **Estrutura da Planilha**
Crie um arquivo `dados_clientes.xlsx` com a seguinte estrutura:

| Nome | Valor | CPF | Vencimento |
|------|-------|-----|------------|
| João Silva | 1500.00 | 12345678901 | 2024-01-15 |
| Maria Santos | 2300.50 | 98765432100 | 2024-01-20 |

### ✅ **Requisitos**
- **Nome**: Nome completo do cliente
- **Valor**: Valor monetário (formato numérico)
- **CPF**: 11 dígitos sem formatação
- **Vencimento**: Data no formato AAAA-MM-DD

---

## 🎛️ Opções de Processamento

### 1. 📋 **Processar TODOS os clientes**
```
Situação: Planilha pequena (< 50 clientes)
Recomendação: Use para processamento completo
```

### 2. 🔢 **Processar primeiros N clientes**
```
Situação: Teste ou processamento parcial
Exemplo: "Processar apenas os primeiros 10 clientes"
Ideal para: Validação inicial
```

### 3. 📦 **Processar em lotes**
```
Situação: Volume alto ou conexão instável
Exemplo: "Processar de 5 em 5 clientes"
Benefício: Pausas entre lotes, menor risco de bloqueio
```

### 4. 🎯 **Processar intervalo específico**
```
Situação: Clientes específicos
Exemplo: "Do 10º ao 25º cliente"
Uso: Quando quer pular alguns clientes
```

### 5. ▶️ **Continuar de onde parou**
```
Situação: Execução interrompida
Exemplo: "Continuar do 20º cliente"
Benefício: Não perde progresso anterior
```

---

## 💡 Recomendações por Volume

### 🔥 **Alto Volume (100+ clientes)**
```bash
Opção recomendada: 3 (Lotes)
Tamanho do lote: 5-10 clientes
Tempo estimado: 2-3 horas
```

### ⚡ **Médio Volume (20-100 clientes)**
```bash
Opção recomendada: 3 (Lotes)
Tamanho do lote: 10-15 clientes
Tempo estimado: 30-60 minutos
```

### 🚀 **Baixo Volume (< 20 clientes)**
```bash
Opção recomendada: 1 (Todos)
Tempo estimado: 5-15 minutos
```

---

## 📊 Resultado e Relatório

### 📈 **Arquivo de Saída**
O sistema gera `planilha_fechamento.xlsx` com:

| Campo | Descrição |
|-------|-----------|
| **Nome** | Nome do cliente |
| **Valor** | Valor original |
| **CPF** | CPF do cliente |
| **Vencimento** | Data de vencimento |
| **Status** | Em dia / Pendente / Erro |
| **Data Pagamento** | Data do pagamento (se em dia) |
| **Método Pagamento** | Cartão / Boleto (se em dia) |

### 📱 **Durante a Execução**
```
🔄 Processando lote 1/5
Processando cliente 1/50: João Silva (CPF: 12345678901)
  ✓ Cliente em dia - Pagamento: 15/01/2024 via Cartão
Processando cliente 2/50: Maria Santos (CPF: 98765432100)
  ⚠ Cliente com pagamento pendente
...
✅ Lote 1 concluído!
Pressione Enter para continuar com o próximo lote ou 'q' para parar:
```

---

## 🛡️ Boas Práticas

### ✅ **Recomendações**
- **Backup**: Sempre faça backup da planilha original
- **Teste**: Execute primeiro com poucos clientes
- **Horário**: Evite horários de pico (9h-12h, 14h-17h)
- **Conexão**: Use conexão estável e rápida
- **Paciência**: Não feche o navegador manualmente

### ⚠️ **Cuidados**
- **Rate Limiting**: Respeite os limites do site
- **Dados Sensíveis**: CPFs são dados pessoais protegidos
- **Legal**: Use apenas com autorização dos clientes
- **Monitoramento**: Acompanhe logs para identificar problemas

### 🚫 **O que NÃO fazer**
- ❌ Fechar o navegador durante execução
- ❌ Processar mais de 20 clientes seguidos sem pausa
- ❌ Executar múltiplas instâncias simultaneamente
- ❌ Usar em horários de manutenção do site

---

## 🚨 Solução de Problemas

### ❌ **Programa Travou**
```bash
1. Pressione Ctrl+C no terminal
2. Execute novamente: ./executar.sh
3. Escolha opção 5: "Continuar de onde parou"
```

### 🐌 **Muito Lento**
```bash
1. Diminua o tamanho do lote (3-5 clientes)
2. Verifique conexão com internet
3. Feche outros programas pesados
4. Tente em horário alternativo
```

### 🔄 **Recomeçar do Zero**
```bash
1. Delete: planilha_fechamento.xlsx
2. Execute: ./executar.sh
3. Escolha a opção desejada
```

### 🌐 **Erro de Site**
```bash
Aguarde alguns minutos e tente novamente
O site pode estar temporariamente indisponível
```

---

## 📞 Suporte

### 🆘 **Precisa de Ajuda?**
- 📧 **Email**: [seu-email@exemplo.com]
- 💬 **GitHub Issues**: [Criar issue no repositório]
- 📖 **Documentação**: Consulte README.md completo

### 📈 **Feedback**
Sua experiência é importante! Relate bugs, sugestões ou melhorias através do GitHub Issues.

---

*Desenvolvido com ❤️ por [Jonatas Pimenta](https://github.com/jonatas-pimenta)*
