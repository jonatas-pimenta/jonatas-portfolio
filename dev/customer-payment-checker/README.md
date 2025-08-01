# 🚀 Customer Payment Checker

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white)
![Shell Script](https://img.shields.io/badge/Shell_Script-121011?style=flat&logo=gnu-bash&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)

**Sistema automatizado para verificação de status de pagamentos via web scraping**

[🚀 Instalação](#-instalação) • [💼 Funcionalidades](#-funcionalidades) • [🎯 Demo](#-demonstração) • [💼 Para Recrutadores](#-valor-para-recrutadores)

</div>

---

## 📋 Sobre o Projeto

Automatiza a verificação de status de pagamentos de clientes através de web scraping, eliminando trabalho manual repetitivo. O sistema processa planilhas Excel e consulta dados em site externo com múltiplas opções de processamento.

### Principais Recursos
- **Automação Web** com Selenium WebDriver
- **Processamento de Planilhas** Excel com OpenPyXL
- **Interface CLI** amigável com múltiplas opções
- **Sistema de Recuperação** para execuções interrompidas

---

## 🛠️ Tecnologias Utilizadas

| Tech | Versão | Uso |
|------|--------|-----|
| ![Python](https://img.shields.io/badge/Python-3.12.3-blue?logo=python) | 3.12.3 | Core + POO |
| ![Selenium](https://img.shields.io/badge/Selenium-4.15.2-green?logo=selenium) | 4.15.2 | Web Scraping |
| ![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.1.2-orange) | 3.1.2 | Excel Processing |

**Ambiente de Desenvolvimento:**
- Python 3.12+ | Chrome 138+ | Ubuntu 24.04.2 LTS *(testado)*

---

## 🎬 Demonstração em Vídeo

<div align="center">

[![Clique aqui para ver o vídeo](https://img.shields.io/badge/Clique_aqui-Para_ver_o_vídeo-red?style=for-the-badge&logo=youtube)](https://drive.google.com/file/d/1QxIY7Ozb4DPTw0iVlhzbp3lg-bFSkKBC/view?usp=drive_link)

*Demonstração completa: Interface, automação Selenium, processamento de dados e geração de relatórios*

</div>

**O que você verá no vídeo:**
- Interface amigável do sistema
- Configuração automática do ambiente
- Automação web com Selenium
- Processamento de dados em tempo real
- Geração de relatórios Excel

---

## 💼 Funcionalidades

### Controles de Processamento
- **Processamento Total** - Todos os clientes
- **Processamento Limitado** - Primeiros N clientes  
- **Processamento em Lotes** - Grupos com pausas
- **Intervalo Específico** - Do cliente X ao Y
- **Continuação** - Retomar execuções interrompidas

### Recursos Avançados
- **Rate Limiting** - Proteção anti-bloqueio automática
- **Sistema de Recovery** - Tolerância a falhas e reconexão
- **Validação de Dados** - Verificação de CPF e formato
- **Interface Progressiva** - Feedback visual em tempo real
- **Logs Detalhados** - Rastreamento completo de operações

---

## 🎯 Demonstração

```bash
$ ./executar.sh

📋 Prévia: 50 clientes carregados
🔧 Opções: [1] Todos [2] Primeiros N [3] Lotes [4] Intervalo [5] Continuar
Escolha: 3 | Lote: 10

📦 Processando lote 1/5
  ✓ João Silva - Em dia (15/01/2024 via Cartão)
  ⚠ Maria Santos - Pendente
✅ Lote concluído!
```

**Resultado:** Planilha Excel com status, datas e métodos de pagamento.

---

## 📋 Pré-requisitos

- **Python 3.8+** (testado em 3.12.3)
- **Google Chrome** versão 138+ instalado
- **Sistema Operacional:** Ubuntu 24.04.2 LTS *(recomendado)*
- **Memória:** 4GB RAM mínimo para processamento fluido
- **Conectividade:** Internet estável para consultas web

---

## 🚀 Instalação

### Instalação Automática (Recomendada)
```bash
git clone [seu-repo] && cd customer-payment-checker
chmod +x executar.sh
./executar.sh
```

### Instalação Manual
```bash
# 1. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar sistema
python verificador_pagamentos.py
```

---

## 💻 Como Usar

### Execução via Script (Recomendado)
```bash
./executar.sh
```

### Execução Direta
```bash
python verificador_pagamentos.py
```

**Opções disponíveis:**
1. **Escolher quantidade** - Define número específico de clientes
2. **Processar todos** - Executa a planilha completa
3. **Cancelar** - Sair do sistema

---

## 📁 Estrutura do Projeto

```
customer-payment-checker/
├── verificador_pagamentos.py    # Sistema principal
├── executar.sh                  # Script de execução
├── requirements.txt             # Dependências Python
├── dados_clientes.xlsx          # Planilha de entrada (exemplo)
├── planilha_fechamento.xlsx     # Resultados gerados
├── .venv/                       # Ambiente virtual
├── README.md                    # Documentação
└── PARA_RECRUTADORES.md         # Análise técnica
```

---

## 📊 Formato das Planilhas

### Entrada (dados_clientes.xlsx)
| Nome | Valor | CPF | Vencimento |
|------|-------|-----|------------|
| João Silva | 1500.00 | 12345678901 | 2024-01-15 |

### Saída (planilha_fechamento.xlsx)
| Nome | CPF | Valor | Status |
|------|-----|-------|--------|
| João Silva | 123.456.789-01 | R$ 1.500,00 | Em dia |

---

## 💼 Valor para Recrutadores

### Competências Demonstradas
- **Web Scraping Avançado** - Selenium WebDriver com tratamento de erros
- **Processamento de Dados** - Manipulação de planilhas Excel
- **Interface de Usuário** - CLI intuitiva e progressiva
- **Arquitetura de Software** - Código modular e bem estruturado
- **Tratamento de Erros** - Sistema robusto com recovery automático

### Aplicabilidade Profissional
- **Automação de Processos** - Substituição de tarefas manuais
- **Integração de Sistemas** - Ponte entre planilhas e sistemas web
- **Business Intelligence** - Coleta e organização de dados empresariais
- **Otimização Operacional** - Redução de tempo em processos repetitivos

**[→ Ver análise técnica completa](./PARA_RECRUTADORES.md)**

---

## 🔗 Conecte-se

<div align="center">

**Desenvolvido por [Jonatas Pimenta](https://github.com/jonatas-pimenta)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)](https://github.com/jonatas-pimenta)

**🎯 Projeto para demonstração de competências em automação Python**

</div>
