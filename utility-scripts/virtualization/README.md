# Scripts de Gerenciamento de Hipervisores no Linux

Coleção de scripts Shell para gerenciar conflitos entre hipervisores no Linux (KVM e VirtualBox) e otimizar ambientes de virtualização. O projeto resolve um problema técnico comum: a impossibilidade de usar simultaneamente dois hipervisores que competem pelos recursos de virtualização do processador.

## Arquitetura Implementada

O projeto implementa uma abordagem modular com detecção automática de hardware e gerenciamento de módulos do kernel do Linux.

<p align="center">
  <img src="https://img.shields.io/badge/Shell-Bash-green?logo=gnu-bash&logoColor=white" alt="Bash">
  <img src="https://img.shields.io/badge/Linux-Kernel-orange?logo=linux&logoColor=white" alt="Linux">
  <img src="https://img.shields.io/badge/Virtualization-KVM%20%26%20VirtualBox-blue?logo=virtualbox&logoColor=white" alt="Virtualization">
</p>

| Componente | Detalhe Técnico | Função Principal |
| :--- | :--- | :--- |
| **Plataforma** | Linux com suporte a KVM | Sistema operacional base para virtualização |
| **Interpretador** | Bash Shell Script | Execução de comandos do SO e manipulação de módulos |
| **Gerenciamento de Módulos** | modprobe e rmmod | Carregamento e descarregamento de drivers de virtualização |
| **Detecção de CPU** | /proc/cpuinfo | Identificação automática de Intel vs AMD |
| **Privilégios** | sudo | Escalação de permissão para operações do kernel |
| **Compatibilidade** | Ubuntu 20.04+, Debian 11+, CentOS 8+, Arch | Suporte multi-distribuição Linux |

## Principais Funcionalidades

**Detecção Automática de Hardware**
- Verificação de tipo de processador (Intel VMX vs AMD-V)
- Identificação de módulos KVM carregados
- Validação de suporte a virtualização no processador

**Gerenciamento de Módulos KVM**
- Desativação ordenada de módulos KVM (kvm_intel/kvm_amd → kvm)
- Verificação de dependências e módulos em uso
- Feedback visual do progresso de execução

**Escalação Automática de Privilégios**
- Detecção de permissões insuficientes
- Re-execução com sudo quando necessário
- Solicitação de senha apenas quando obrigatório

**Compatibilidade Multi-Distribuição**
- Testes em Ubuntu, Debian, CentOS, RHEL, Arch Linux
- Detecção automática de gerenciador de pacotes
- Comportamento consistente entre distribuições

**Reversibilidade**
- Scripts reutilizáveis para reativar hipervisores
- Alternativa via reinicialização do sistema
- Documentação clara de procedimentos de rollback



## Aplicação Profissional / Valor para Empresas

Ambientes de virtualização são críticos em operações de TI, infraestrutura moderna e desenvolvimento de software. A capacidade de gerenciar múltiplos hipervisores e resolver conflitos de recursos é essencial para profissionais de DevOps, administradores de sistemas e arquitetos de infraestrutura.

Valores empresariais entregues:
- Eliminação de downtime causado por conflitos de hipervisores
- Aumenta flexibilidade operacional ao suportar múltiplas plataformas de virtualização
- Automatização de tarefas repetitivas reduzindo erros manuais
- Documentação de procedimentos complexos para transferência de conhecimento
- Manutenção simplificada de ambientes de produção e desenvolvimento
- Base para automação de infraestrutura em escala

## Competências Técnicas Demonstradas

- **Shell Script Avançado:** Bash com detecção de condições, loops e tratamento de erros
- **Administração Linux:** Manipulação de módulos do kernel, gerenciamento de privilégios
- **Gerenciamento de Hipervisores:** Compreensão profunda de KVM e VirtualBox
- **Hardware Virtualization:** Conhecimento de VMX (Intel) e AMD-V
- **Escalação de Privilégios:** Implementação segura de sudo com verificação prévia
- **Detecção de Hardware:** Leitura e parsing de /proc/cpuinfo
- **Debugging e Troubleshooting:** Mensagens informativas e logging de operações
- **Compatibilidade Multi-Distribuição:** Testes e suporte para múltiplas distribuições Linux
- **Documentação Técnica:** Explicações claras de problemas complexos e soluções
- **DevOps Mindset:** Automação de processos recorrentes e repetitivos

## 📁 Estrutura do Projeto

```
virtualization/
├── desativar_kvm.sh         # Script principal para desativar KVM
├── README.md                # Documentação
└── [futuro] ativar_kvm.sh   # Script para reativar KVM
```

## 🔧 Demonstração Técnica

### Problema: Conflito de Hipervisores

Quando tanto KVM quanto VirtualBox estão ativos, o processador não consegue dedicar seus recursos de virtualização (VMX para Intel, AMD-V para AMD) a ambos simultaneamente:

```
Processador Intel com VMX
├── KVM (ativo) - MONOPOLIZA VMX
└── VirtualBox (tenta usar) - ERRO VERR_VMX_IN_VMX_ROOT_MODE ❌
```

### Solução: Desativar Módulos do Kernel

O script remove os módulos do KVM em ordem de dependência:

```bash
# Módulos do kernel para virtualização
lsmod | grep kvm
# kvm_intel              20480  2
# kvm                   765952  1 kvm_intel

# Ordem correta de remoção:
# 1. kvm_intel (depende de kvm)
# 2. kvm (módulo principal)
```

### Exemplo de Código: Detecção de CPU

```bash
# Detectar tipo de processador
if grep -q "vmx" /proc/cpuinfo; then
    echo "Processador Intel com VMX detectado"
    CPU_MODULE="kvm_intel"
elif grep -q "svm" /proc/cpuinfo; then
    echo "Processador AMD com SVM detectado"
    CPU_MODULE="kvm_amd"
else
    echo "Erro: Virtualização não suportada"
    exit 1
fi
```

### Exemplo de Código: Escalação de Privilégios Segura

```bash
# Verificar se já é root
if [[ $EUID -ne 0 ]]; then
    echo "Permissão de administrador necessária."
    sudo "$0"  # Re-executar script com sudo
    exit $?
fi
```

### Exemplo de Código: Remoção Ordenada de Módulos

```bash
# Remover módulos na ordem correta (dependência reversa)
echo "Desativando módulos KVM..."

# Primeiro remover o módulo específico da CPU
if lsmod | grep -q "$CPU_MODULE"; then
    rmmod "$CPU_MODULE"
    echo "✓ Módulo '$CPU_MODULE' removido"
fi

# Depois remover o módulo principal
if lsmod | grep -q "^kvm"; then
    rmmod kvm
    echo "✓ Módulo 'kvm' removido"
fi
```

### Workflow Completo

1. **Verificação:** Script detecta se é necessário elevar privilégios
2. **Detecção:** Identifica tipo de CPU (Intel/AMD) via /proc/cpuinfo
3. **Validação:** Confirma que módulos KVM estão carregados
4. **Remoção:** Descarrega módulos na ordem correta
5. **Confirmação:** Feedback visual do sucesso da operação
6. **Reversão:** Documentação de como reativar KVM

## 💡 Desafios e Soluções (Troubleshooting)

**Desafio 1: Módulos KVM em Uso (Busy)**

- **Problema:** Ao tentar remover módulo KVM, erro "Module in use" porque VMs estão rodando em KVM.
- **Solução:** Script verifica se VMs KVM estão ativas antes de desativar. Se necessário, usuário deve parar as VMs primeiro com `virsh shutdown` ou `virsh destroy`.

**Desafio 2: Falta de Permissões para modprobe/rmmod**

- **Problema:** Usuário comum não consegue manipular módulos do kernel.
- **Solução:** Script detecta EUID (Effective UID) e solicita sudo automaticamente, re-executando a si mesmo com privilégios elevados.

**Desafio 3: Diferentes Nomes de Módulos Entre Distribuições**

- **Problema:** Algumas distribuições podem nomear ou organizar módulos diferentemente.
- **Solução:** Script verifica o arquivo /proc/cpuinfo (padrão em todas as distros) para identificar corretamente se é Intel ou AMD, ao invés de depender de nomes de módulos inconsistentes.

**Desafio 4: Reversão Sem Reinicializar**

- **Problema:** Usuário precisava recarregar módulos KVM após usar VirtualBox.
- **Solução:** Documentação inclui comando `modprobe` para recarregar módulos manualmente, evitando necessidade de reinicialização completa.

## ⚡ Como Usar

### Execução Simples

```bash
# Torne executável (primeira vez)
chmod +x desativar_kvm.sh

# Execute
./desativar_kvm.sh
```

### Reativar KVM (sem reiniciar)

```bash
# Recarregar módulos manualmente
sudo modprobe kvm
sudo modprobe kvm_intel  # ou kvm_amd para AMD
```

### Verificar Status

```bash
# Ver módulos ativos
lsmod | grep kvm

# Ver status de virtualização no processador
grep -E "vmx|svm" /proc/cpuinfo
```

---

<div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>
