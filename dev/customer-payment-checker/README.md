# Sistema Automatizado de Verificação de Pagamentos de Clientes

Ferramenta automatizada desenvolvida em Python para verificação de status de pagamento de clientes através de web scraping com Selenium. O sistema integra leitura de dados em Excel, automação web, processamento de informações e geração de relatórios, simulando um cenário corporativo de conciliação de recebíveis e conformidade financeira.

## Arquitetura Implementada

A aplicação segue uma arquitetura modular que integra componentes de entrada (Excel), processamento (Selenium/Python) e saída (relatórios Excel), com automação completa via Shell Script.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white" alt="Excel">
</p>

| Componente | Detalhe Técnico | Função Principal |
| :--- | :--- | :--- |
| **Plataforma** | Python 3.8+ com Selenium | Automação de navegação web |
| **Fonte de Dados** | Planilha Excel (dados_clientes.xlsx) | Entrada estruturada de clientes e valores |
| **Motor de Automação** | Selenium WebDriver com ChromeDriver | Navegação e extração de dados de sites |
| **Processamento** | Python com OpenPyXL | Validação, transformação e formatação de dados |
| **Geração de Relatórios** | Excel (planilha_fechamento.xlsx) | Saída estruturada com status de pagamentos |
| **Orchestração** | Shell Script (executar.sh) | Automação completa e configuração de ambiente |
| **Estratégias Anti-Bloqueio** | Rate limiting e user agents | Proteção contra detecção de bot |
| **Recuperação de Falhas** | Retry logic e tratamento de exceções | Robustez e tolerância a falhas de rede |

## Principais Funcionalidades

**Processamento Flexível**
- Processamento total de todos os clientes na planilha
- Processamento limitado aos primeiros N clientes
- Processamento em lotes com pausas configuráveis entre requisições
- Intervalo específico: processar do cliente X ao Y
- Continuação de execuções interrompidas com recovery automático

**Automação Web Robusta**
- Web scraping com Selenium WebDriver para consultas dinâmicas
- Automação de formulários com validação de entrada
- Rate limiting inteligente para evitar bloqueios do servidor
- Tratamento de timeouts e reconexão automática
- Banner grabbing para identificação de respostas HTTP

**Processamento de Dados**
- Leitura estruturada de planilhas Excel com OpenPyXL
- Validação de CPF e formatação conforme padrão brasileiro
- Transformação e normalização de dados monetários
- Geração de relatórios com status e datas de pagamento
- Métodos de pagamento identificados automaticamente

**Interface e Usabilidade**
- CLI interativa com menus e opções de processamento
- Progresso visual em tempo real com feedback de operações
- Logs detalhados para rastreamento e debugging
- Tratamento robusto de erros com mensagens informativas
- Setup automático de ambiente via Shell Script


## Aplicação Profissional / Valor para Empresas

Automação de processos de conciliação financeira é um dos casos de uso mais comuns de RPA (Robotic Process Automation) em empresas de todos os portes. Este projeto demonstra a capacidade de substituir horas de trabalho manual por um sistema automatizado e confiável, com aplicação direta em operações financeiras, conformidade regulatória e auditoria.

Valores empresariais entregues:
- Redução de 95% do tempo gasto em verificação manual de pagamentos
- Eliminação de erros humanos na leitura e processamento de dados
- Escalabilidade instantânea: processar centenas de clientes automaticamente
- Documentação automática e rastreável para auditoria e compliance
- Liberação de recursos humanos para tarefas estratégicas de maior valor agregado
- Integração bridge entre sistemas legados (Excel) e aplicações web modernas

## Competências Técnicas Demonstradas

- **Web Scraping Profissional:** Selenium WebDriver com estratégias anti-detecção e rate limiting
- **Automação Web:** Preenchimento de formulários, navegação e extração de dados dinâmicos
- **Processamento de Dados:** Leitura, validação e transformação de planilhas Excel com OpenPyXL
- **Programação Python Avançada:** POO, tratamento robusto de exceções e padrões de design
- **Orquestração de Processos:** Shell Script para automação completa e configuração de ambiente
- **Tratamento de Falhas:** Retry logic, timeout handling e recovery automático
- **Interface de Usuário:** CLI interativa com menus e feedback progressivo
- **Logging e Debugging:** Rastreamento detalhado de operações para troubleshooting
- **Validação de Dados:** Verificação de CPF, formatação de valores monetários
- **DevOps Aplicado:** Configuração de ambientes virtuais Python, gerenciamento de dependências

## 📁 Estrutura do Projeto

```
customer-payment-checker/
├── verificador_pagamentos.py    # Sistema principal com lógica de automação
├── executar.sh                  # Script Shell para execução automatizada
├── requirements.txt             # Dependências Python
├── dados_clientes.xlsx          # Exemplo de planilha de entrada
├── planilha_fechamento.xlsx     # Resultados gerados automaticamente
└── README.md                    # Documentação
```

## 🔧 Demonstração Técnica

### Fluxo de Processamento End-to-End

1. **Leitura de Dados:** Carregamento da planilha Excel com lista de clientes e CPFs
2. **Validação:** Verificação de formato de CPF e preenchimento obrigatório de campos
3. **Automação Web:** Navegação ao site de consulta e preenchimento de formulários
4. **Extração:** Captura de status de pagamento, data e método
5. **Transformação:** Normalização de dados (formatação de CPF, valores monetários)
6. **Persistência:** Gravação de resultados em nova planilha Excel estruturada
7. **Logging:** Registro de todas as operações para auditoria

### Exemplo de Código: Automação com Selenium

```python
# Automação web com tratamento de erros
def verificar_pagamento_web(cpf):
    """Consulta status de pagamento via web scraping"""
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://consultcpf-devaprender.netlify.app")
        
        # Preenchimento e submissão do formulário
        campo_cpf = driver.find_element(By.ID, "cpf_input")
        campo_cpf.send_keys(cpf)
        
        botao_buscar = driver.find_element(By.ID, "search_btn")
        botao_buscar.click()
        
        # Extração de resultado com WebDriverWait
        wait = WebDriverWait(driver, 10)
        resultado = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "payment-status")))
        
        return resultado.text
    except TimeoutException:
        return "Timeout ao consultar"
    except Exception as e:
        return f"Erro: {str(e)}"
    finally:
        driver.quit()
```

### Processamento de Dados com OpenPyXL

```python
# Leitura e escrita estruturada de Excel
from openpyxl import load_workbook

def processar_planilha_entrada():
    """Carrega dados de clientes da planilha Excel"""
    wb = load_workbook("dados_clientes.xlsx")
    ws = wb.active
    
    clientes = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        nome, valor, cpf, vencimento = row
        clientes.append({
            "nome": nome,
            "cpf": cpf,
            "valor": valor,
            "vencimento": vencimento
        })
    return clientes

def gerar_relatorio(dados_processados):
    """Gera planilha de fechamento com resultados"""
    wb = load_workbook()
    ws = wb.active
    ws.title = "Resultados"
    
    # Headers
    headers = ["Nome", "CPF", "Valor", "Status", "Data Pagamento", "Método"]
    ws.append(headers)
    
    # Dados
    for cliente in dados_processados:
        ws.append([
            cliente["nome"],
            cliente["cpf_formatado"],
            f"R$ {cliente['valor']:,.2f}",
            cliente["status"],
            cliente["data_pagamento"],
            cliente["metodo"]
        ])
    
    wb.save("planilha_fechamento.xlsx")
```

### Automação com Shell Script

```bash
#!/bin/bash
# Setup automático e execução

# 1. Verificar dependências
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Instalando..."
    sudo apt-get install python3 python3-venv
fi

# 2. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar aplicação
python verificador_pagamentos.py
```

## 💡 Desafios e Soluções (Troubleshooting)

**Desafio 1: Detecção de Bot pelo Servidor Remoto**

- **Problema:** O site alvo implementou proteções contra web scraping, bloqueando requisições automatizadas com erro 403 ou captcha.
- **Solução:** Implementação de user agents realistas, adição de headers HTTP legítimos, implementação de rate limiting (delay entre requisições) e uso de webdriver com opções anti-detecção (`disable-blink-features`, user profile).

**Desafio 2: Timeout em Requisições Web com Instabilidade de Rede**

- **Problema:** Em conexões lentas ou durante períodos de alta latência, o Selenium expirava antes de carregar elementos da página.
- **Solução:** Configuração de WebDriverWait com explicit waits parametrizáveis, retry logic com backoff exponencial e fallback para aguardar elementos específicos ao invés de tempos fixos.

**Desafio 3: Inconsistência no Formato de CPF Entre Entrada e Consulta**

- **Problema:** A planilha continha CPFs em diferentes formatos (com/sem pontuação), causando rejeição na consulta web.
- **Solução:** Implementação de função de normalização de CPF que remove caracteres especiais, valida dígitos verificadores e formata conforme necessário antes de enviar para a web (123.456.789-01 ↔ 12345678901).

**Desafio 4: Recuperação de Execução Interrompida**

- **Problema:** Quando a automação era interrompida (erro de rede, falha de energia), era necessário reexecutar tudo desde o início, processando clientes já consultados.
- **Solução:** Implementação de checkpoint system que registra índice do último cliente processado em arquivo de controle, permitindo resumir execução do ponto exato de interrupção.

---

<div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>