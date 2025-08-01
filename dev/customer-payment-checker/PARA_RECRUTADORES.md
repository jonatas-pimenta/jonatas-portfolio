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

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green?logo=selenium)
![Excel](https://img.shields.io/badge/OpenPyXL-Excel_Processing-orange)
![Chrome](https://img.shields.io/badge/Chrome-138+-yellow?logo=googlechrome)

**Ambiente de Desenvolvimento:**
- Python 3.12+ | Chrome 138+ | Ubuntu 24.04.2 LTS *(testado)*

---

## 🎬 Demonstração em Vídeo

<div align="center">

<a href="https://drive.google.com/file/d/1QxIY7Ozb4DPTw0iVlhzbp3lg-bFSkKBC/view?usp=drive_link" target="_blank">
  <img src="https://img.shields.io/badge/Assistir_Vídeo_Demo-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Assistir vídeo de demonstração">
</a>

<p style="margin-top: 12px;">
💡 <em>Clique no botão acima e veja código virando resultado — em execução real.</em>
</p>

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

### Automação Web
- **Navegação Inteligente** - Abertura e fechamento controlado
- **Preenchimento Automático** - Formulários web via Selenium
- **Captura de Dados** - Extração de informações estruturadas
- **Tratamento de Erros** - Gestão de timeouts e falhas de rede

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

### Execução Direta
```bash
python verificador_pagamentos.py
```

### Execução via Script (Recomendado)
```bash
./executar.sh
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
├── planilha_fechamento.xlsx     # Resultados gerados apos executar o script
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

## 🔧 Configuração Avançada

<details>
<summary><strong>Personalizar Configurações</strong></summary>

```python
# verificador_pagamentos.py - Configurações principais

# Timeouts e intervalos
TIMEOUT_PADRAO = 10  # segundos
INTERVALO_ENTRE_CONSULTAS = 2  # segundos

# Configurações do Chrome
chrome_options.add_argument("--headless")  # Executar sem interface gráfica
chrome_options.add_argument("--window-size=1920,1080")

# Site de consulta
URL_CONSULTA = "https://consultcpf-devaprender.netlify.app"
```

</details>

---

## 🎓 Valor para Recrutadores

### Competências Demonstradas
- **Web Scraping Avançado** - Selenium WebDriver com tratamento de erros
- **Processamento de Dados** - Manipulação de planilhas Excel
- **Interface de Usuário** - CLI intuitiva e progressive
- **Arquitetura de Software** - Código modular e bem estruturado
- **Tratamento de Erros** - Sistema robusto com recovery automático

### Aplicabilidade Profissional
- **Automação de Processos** - Substituição de tarefas manuais
- **Integração de Sistemas** - Ponte entre planilhas e sistemas web
- **Business Intelligence** - Coleta e organização de dados empresariais
- **Otimização Operacional** - Redução de tempo em processos repetitivos

**[→ Ver análise técnica completa](./PARA_RECRUTADORES.md)**

---

## 🔗 Conecte-se Comigo

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)](https://github.com/jonatas-pimenta)

</div>