# 💾 Backup Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnu-bash&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-FF6B35?style=flat&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)

**Sistema de backup com interface gráfica Python e engine robusta em Bash**

[🚀 Instalação](#-como-executar) • [💼 Funcionalidades](#-funcionalidades) • [🎯 Arquitetura](#-arquitetura-do-sistema) • [💼 Para Recrutadores](#-valor-para-recrutadores)

</div>

---

## 📋 Descrição do Projeto

O **Backup Manager** é uma aplicação completa para Linux que permite realizar backups de arquivos ou pastas de forma eficiente, com interface gráfica amigável desenvolvida em Python (Tkinter). O backup é realizado utilizando o comando `rsync` para arquivos ou script Bash (`backup_engine.sh`) para pastas, garantindo máxima eficiência e confiabilidade.

O sistema mantém um histórico completo de todas as operações de backup realizadas, mesmo após fechar o programa, facilitando o acompanhamento e auditoria das operações. Desenvolvido com foco em usabilidade e robustez para ambientes de produção.

---

## 🏗️ Arquitetura do Sistema

<p align="center">
  <img src="screenshots/interface-main.png" width="70%" alt="Interface Principal do Backup Manager">
</p>

### 🔧 **Fluxo de Operação**

```
┌─────────────────────────┐    subprocess    ┌─────────────────────────┐
│     Python GUI          │ ===============> │    Bash Engine          │
│    (backup_gui.py)      │                  │  (backup_engine.sh)     │
│                         │                  │                         │
│ • Interface Tkinter     │                  │ • rsync operations      │
│ • Seleção arquivo/pasta │                  │ • Error handling        │
│ • Threading para UI     │                  │ • Progress tracking     │
│ • Histórico visual      │                  │ • Lock file prevention │
│ • Proteção com senha    │                  │ • Log detalhado         │
└─────────────────────────┘                  └─────────────────────────┘
            │                                             │
            └─────────────────┬───────────────────────────┘
                              │
                    ┌─────────────────────┐
                    │   Sistema de Logs   │
                    │ (backup_history.log)│
                    │                     │
                    │ • Histórico contínuo│
                    │ • Timestamps        │
                    │ • Status tracking   │
                    │ • Separadores       │
                    └─────────────────────┘
```

**Características Técnicas:**
- **Dual Mode:** rsync direto para arquivos, script Bash para pastas
- **Threading:** Interface não trava durante operações
- **Histórico Persistente:** Logs mantidos entre sessões
- **Proteção de Dados:** Sistema de senha para limpeza de logs
- **Real-time Feedback:** Status e erros exibidos instantaneamente

---

## 💼 Funcionalidades

### 🎯 **Interface Gráfica Moderna**
- **Navegador integrado** - Seleção fácil de origem e destino
- **Dual mode selection** - Escolha entre backup de arquivo ou pasta
- **Real-time logging** - Log detalhado exibido na tela durante operação
- **Histórico visual** - Carregamento automático de backups anteriores

### 🔧 **Engine de Backup Inteligente**
- **rsync otimizado** - Para arquivos individuais (rápido e eficiente)
- **Script Bash robusto** - Para pastas (controle total do processo)
- **Proteção contra concorrência** - Sistema de lock files
- **Verificações de segurança** - Validação de origem e destino

### 📊 **Sistema de Auditoria**
- **Histórico contínuo** - Registro de todas as operações em `backup_history.log`
- **Timestamps precisos** - Data e hora de cada operação
- **Status detalhado** - Sucesso, falhas e mensagens de erro
- **Proteção com senha** - Limpeza segura do log visual

### ⚙️ **Recursos Avançados**
- **Threading assíncrono** - Interface responsiva durante backups
- **Mensagens em tempo real** - Status e progresso instantâneos
- **Persistência de dados** - Histórico mantido entre sessões
- **Error handling robusto** - Tratamento completo de exceções

---

## 📋 Pré-requisitos

- **Python 3.6+** com Tkinter
- **Bash** (shell padrão Linux)
- **rsync** (geralmente já instalado)
- **Sistema operacional:** Linux

### Verificação de Dependências
```bash
# Verificar Python e Tkinter
python3 -c "import tkinter; print('Tkinter OK')"

# Verificar rsync
rsync --version

# Verificar Bash
bash --version
```

---

## 🚀 Como Executar

### 1. Preparação do Ambiente
```bash
# Clone o repositório
git clone https://github.com/jonatas-pimenta/jonatas-portfolio.git
cd devops/backup-manager

# (Opcional) Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate
```

### 2. Configuração de Permissões
```bash
# Dar permissão de execução ao script Bash
chmod +x backup_engine.sh
```

### 3. Execução da Aplicação
```bash
# Executar interface gráfica
python3 backup_gui.py
```

### 4. Usando a Interface
1. **Escolher tipo** - Selecione "Arquivo" ou "Pasta" para backup
2. **Selecionar origem** - Use o botão "Browse" para escolher o que será copiado
3. **Escolher destino** - Defina onde o backup será salvo
4. **Executar backup** - Clique em "Run Backup" e acompanhe o progresso
5. **Verificar histórico** - O log completo fica em `backup_history.log`

---

## 📁 Estrutura do Projeto

```
backup-manager/
├── backup_gui.py           # Interface gráfica principal (Python/Tkinter)
├── backup_engine.sh        # Script Bash para backup de pastas usando rsync
├── backup_history.log      # Arquivo de histórico de todos os backups
├── requirements.txt        # Dependências documentadas
├── config.json            # Configurações opcionais
├── screenshots/            # Capturas da interface
│   ├── interface-main.png    # Tela principal
│   └── backup-progress.png   # Progresso do backup
└── README.md              # Esta documentação
```

---

## 🔧 Demonstração Técnica

### Seleção Inteligente de Engine
```python
# backup_gui.py - Escolha automática entre rsync e script Bash
def execute_backup(self):
    if self.backup_type.get() == "arquivo":
        # Usar rsync diretamente para arquivos
        cmd = ['rsync', '-avh', '--progress', source, dest]
    else:
        # Usar script Bash para pastas (maior controle)
        cmd = ['./backup_engine.sh', source, dest]
    
    # Execução em thread separada
    self.run_backup_thread(cmd)
```

### Sistema de Log Persistente
```bash
# backup_engine.sh - Logging estruturado
{
    echo "========================================="
    echo "BACKUP $(date '+%d/%m/%Y %H:%M:%S')"
    echo "Origem: $SOURCE"
    echo "Destino: $DEST"
    echo "Status: $STATUS"
    echo "========================================="
} >> "$LOG_FILE"
```

### Threading para UI Responsiva
```python
# Execução assíncrona para não travar interface
import threading

def run_backup_thread(self, cmd):
    thread = threading.Thread(target=self._execute_backup, args=(cmd,))
    thread.daemon = True
    thread.start()
```

---

## 🔍 Conceitos Demonstrados

### **DevOps e Automação**
- Automação de backup crítico de sistema
- Integração Python + Bash para máxima eficiência
- Sistema de logging para auditoria e compliance
- Proteção contra execução concorrente

### **Desenvolvimento de Interface**
- GUI desktop profissional com Tkinter
- Threading para operações assíncronas
- Real-time feedback e progress tracking
- User experience otimizada para operações técnicas

### **System Administration**
- Uso avançado de rsync para sincronização
- Scripts Bash robustos com error handling
- Gerenciamento de arquivos e permissões
- Estratégias de backup para ambientes produtivos

---

## 📈 Observações Técnicas

- **Histórico Contínuo:** O arquivo `backup_history.log` é criado automaticamente e mantém registro permanente
- **Dual Engine:** Arquivos usam rsync direto; pastas usam script Bash para maior controle
- **Proteção de Dados:** Log visual pode ser limpo, mas histórico em arquivo é preservado
- **Threading Assíncrono:** Interface permanece responsiva durante operações longas
- **Linux Exclusive:** Desenvolvido especificamente para sistemas Linux/Unix

---

## 💼 Valor para Recrutadores

### Competências Demonstradas
- **Python GUI Development** - Tkinter, threading, subprocess integration
- **Bash Scripting Avançado** - rsync automation, error handling, logging
- **DevOps Tools** - Backup automation, system administration
- **System Integration** - Multi-language solution (Python + Bash)
- **User Experience** - Intuitive interface for technical operations
- **Error Handling** - Robust exception management and recovery

### Aplicabilidade Profissional
- **Backup Solutions** - Critical data protection strategies
- **DevOps Automation** - Infrastructure maintenance tools
- **System Administration** - Internal tools development
- **GUI Applications** - Desktop interfaces for system tools
- **Process Automation** - Workflow optimization and reliability

### Casos de Uso Reais
- Backup automatizado de servidores de desenvolvimento
- Ferramentas internas de DevOps para teams
- Interfaces gráficas para scripts administrativos
- Sistema de auditoria e compliance para backups
- Automation tools para rotinas de manutenção

---

## 🤝 Contato e Portfólio

<div align="center">

**Desenvolvido por [Jonatas Pimenta](https://github.com/jonatas-pimenta)**  
Estudante de Redes de Computadores | Buscando oportunidades de estágio em Tecnologia  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

🎯 Este projeto demonstra integração Python+Bash para automação DevOps profissional.

</div>