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


## 📋 Descrição do Projeto

O Verificador de Pagamentos de Clientes é uma ferramenta automatizada desenvolvida em Python que utiliza a biblioteca Selenium para interagir com uma aplicação web externa e verificar o status de pagamento de clientes com base em seus CPFs. O projeto lê dados de uma planilha Excel (dados_clientes.xlsx), processa cada cliente individualmente, consulta o status de pagamento em um site específico ( https://consultcpf-devaprender.netlify.app ) e gera uma planilha de fechamento (planilha_fechamento.xlsx) com os resultados.

Este sistema é ideal para pequenas empresas ou profissionais autônomos que precisam automatizar a verificação de pagamentos, economizando tempo e minimizando erros manuais. Ele oferece flexibilidade no processamento, permitindo verificar todos os clientes ou um número específico.

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
### 🚀 Habilidades Técnicas Aplicadas

**Automação e Web Scraping**
- Web scraping com Selenium WebDriver
- Automação de formulários web
- Controle de tempo e tratamento de falhas

**Manipulação de Dados**
- Leitura e escrita de planilhas Excel com OpenPyXL
- Validação e formatação de dados
- Geração de relatórios automatizados

**Programação**
- Programação Orientada a Objetos com Python
- Interface CLI com menus interativos
- Tratamento robusto de exceções

**DevOps / Ambiente**
- Execução automatizada via Shell Script
- Configuração de ambiente virtual Python (.venv)
- Testado em Ubuntu Server com Google Chrome


## 💼 Funcionalidades

### Controles de Processamento
- **Processamento Total** - Todos os clientes da planilha
- **Processamento Limitado** - Primeiros N clientes  
- **Processamento em Lotes** - Grupos com pausas configuráveis
- **Intervalo Específico** - Do cliente X ao Y
- **Continuação** - Retomar execuções interrompidas

### Recursos Avançados
- **Rate Limiting** - Proteção anti-bloqueio automática
- **Sistema de Recovery** - Tolerância a falhas e reconexão
- **Validação de Dados** - Verificação de CPF e formato
- **Interface Progressiva** - Feedback visual em tempo real
- **Logs Detalhados** - Rastreamento completo de operações
- **Formatação Automática** - CPF e valores monetários

-

**Resultado:** Planilha Excel com status, datas e métodos de pagamento.

---

## 📋 Pré-requisitos

- **Python 3.8+** (testado em 3.12.3)
- **Google Chrome** versão 138+ instalado
- **Sistema Operacional:** Ubuntu 24.04.2 LTS *(recomendado)*
- **Conectividade:** Internet estável para consultas web

---

## 🚀 Instalação

### Instalação Automática (Recomendada)
```bash
git clone https://github.com/jonatas-pimenta/jonatas-portfolio.git
cd dev/customer-payment-checker
chmod +x executar.sh
./executar.sh
```

### Instalação Manual
```bash
# 1. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install selenium openpyxl webdriver-manager

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
1. **Processar todos** - Executa a planilha completa
2. **Processar quantidade específica** - Define número de clientes
3. **Processamento em lotes** - Grupos com pausas
4. **Continuar execução** - Retoma processamento interrompido

---

## 📁 Estrutura do Projeto

```
customer-payment-checker/
├── verificador_pagamentos.py    # Sistema principal
├── executar.sh                  # Script de execução Shell
├── requirements.txt             # Dependências Python
├── dados_clientes.xlsx          # Planilha de entrada (exemplo)
├── planilha_fechamento.xlsx     # Resultados gerados
├── .venv/                       # Ambiente virtual
└── README.md                    # Documentação
```

---

## 📊 Formato das Planilhas

### Entrada (dados_clientes.xlsx)
| Nome | Valor | CPF | Vencimento |
|------|-------|-----|------------|
| João Silva | 1500.00 | 12345678901 | 2024-01-15 |

### Saída (planilha_fechamento.xlsx)
| Nome | CPF | Valor | Status | Data Pagamento | Método |
|------|-----|-------|--------|----------------|---------|
| João Silva | 123.456.789-01 | R$ 1.500,00 | Em dia | 15/01/2024 | Cartão |

---

## 🔍 Conceitos Aplicados

### **Programação Python Avançada**
- Programação Orientada a Objetos
- Manipulação de arquivos Excel com OpenPyXL
- Tratamento robusto de exceções
- Validação e formatação de dados
- Interface de linha de comando interativa

### **Web Scraping Profissional**
- Selenium WebDriver para automação de navegadores
- Estratégias anti-detecção e rate limiting
- Recuperação automática de falhas de conexão
- Parsing de dados web complexos
- Gestão de sessões e cookies

### **Automação e DevOps**
- Scripts Shell para automação completa
- Configuração automática de ambiente
- Integração entre diferentes tecnologias
- Logs estruturados para debugging
- Deploy e execução simplificados

---

## 💼 Valor para Recrutadores

### Competências Demonstradas
- **Web Scraping Avançado** - Selenium WebDriver com tratamento de erros
- **Processamento de Dados** - Manipulação robusta de planilhas Excel
- **Interface de Usuário** - CLI intuitiva e progressiva
- **Arquitetura de Software** - Código modular e bem estruturado
- **Tratamento de Erros** - Sistema robusto com recovery automático
- **Automação Completa** - From zero to hero com scripts Shell

### Aplicabilidade Profissional
- **Automação de Processos** - Substituição de tarefas manuais repetitivas
- **Integração de Sistemas** - Ponte entre planilhas e sistemas web
- **Business Intelligence** - Coleta e organização de dados empresariais
- **Otimização Operacional** - Redução significativa de tempo em processos
- **Escalabilidade** - Sistema preparado para grandes volumes de dados

### Casos de Uso Reais
- Conciliação bancária automatizada
- Verificação de status de cobranças
- Auditoria de recebíveis
- Monitoramento de inadimplência
- Integração com ERPs via web scraping

---

<div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>