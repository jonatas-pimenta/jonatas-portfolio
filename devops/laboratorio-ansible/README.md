# Laboratório Ansible – Automação de Pacotes e Serviços em Linux

Laboratório prático que demonstra automação de configuração com Ansible: instalação de pacotes essenciais e configuração de serviços (Apache2) em hosts Linux gerenciados via SSH. O cenário simula um nó de controle Ansible orquestrando um cliente remoto com idempotência garantida.

## Arquitetura Implementada

Ambiente mínimo com um nó de controle Ansible e um host gerenciado acessado por SSH com chave, aplicando playbook único para pacotes e serviços.

<p align="center">
  <img src="diagrama-arquitetura.png" width="70%" alt="Arquitetura do Laboratório Ansible">
</p>

| Componente | Detalhe Técnico | Função Principal |
| :--- | :--- | :--- |
| **Nó de Controle** | Ansible em Linux (Ubuntu) | Orquestra playbooks via SSH |
| **Host Gerenciado** | Ubuntu/Debian com Python 3 | Recebe configurações e pacotes |
| **Comunicação** | SSH com chave e sudo (become) | Execução remota segura |
| **Inventário** | hosts (ini) | Definição de alvo e variáveis |
| **Playbook** | instalar_programas.yml (YAML) | Tarefas de pacotes e serviços |
| **Módulos** | apt, service | Gestão de pacotes e systemd |

## Principais Funcionalidades

**Gerenciamento de Pacotes**
- Atualização de cache apt
- Instalação de htop, net-tools, curl, tmux, apache2
- Idempotência garantida pelo Ansible

**Gerenciamento de Serviços**
- Start/enable do Apache2 (systemd)
- Verificação de estado de serviço
- Configuração persistente pós-reboot

**Execução Segura**
- SSH por chave + sudo (become)
- Inventário organizado (grupo meus_clientes)
- Interpretador Python configurado por host

## Aplicação Profissional / Valor para Empresas

Automação de configuração é base de operações de TI e DevOps. Este laboratório mostra como padronizar e repetir configurações críticas em servidores Linux com segurança e rastreabilidade.

Valores empresariais entregues:
- Reduz tempo de provisionamento e erros manuais
- Garante consistência entre servidores
- Facilita auditoria e conformidade com registros claros
- Cria base para evolução para roles, múltiplos hosts e CI/CD

## Competências Técnicas Demonstradas

- **Ansible Fundamentals:** Inventário, playbooks, modules apt/service, become
- **Linux Administration:** Gestão de pacotes e serviços em Debian/Ubuntu
- **SSH Hardening:** Acesso remoto com chave e sudo controlado
- **YAML e IaC:** Estruturação declarativa de configuração
- **Idempotência e Compliance:** Execução repetida sem efeitos colaterais
- **Troubleshooting:** Validação de conectividade, logs de execução

## 📁 Estrutura do Projeto

```
laboratorio-ansible/
├── hosts                        # Inventário de hosts
├── instalar_programas.yml       # Playbook principal
├── resultado-playbook.png       # Evidência de execução
├── diagrama-arquitetura.png     # Diagrama do lab
└── README.md
```

## 🔧 Demonstração Técnica

### Inventário (hosts)
```ini
[meus_clientes]
cliente_prod ansible_host=192.168.15.5 ansible_user=osboxes

[meus_clientes:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Playbook Principal (instalar_programas.yml)
```yaml
- name: Instalar pacotes essenciais no cliente
  hosts: meus_clientes
  become: yes
  tasks:
    - name: Atualizar cache do apt
      apt:
        update_cache: yes

    - name: Instalar pacotes
      apt:
        name:
          - htop
          - net-tools
          - curl
          - tmux
          - apache2
        state: present

    - name: Iniciar e ativar o Apache2
      service:
        name: apache2
        state: started
        enabled: yes
```

### Resultado da Execução

<p align="center">
  <img src="resultado-playbook.png" width="80%" alt="Execução do playbook Ansible">
</p>

**Resultado demonstrado:** changed=0, failed=0, apache2 instalado e ativo.

## 💡 Desafios e Soluções (Troubleshooting)

**Desafio 1: Falha de SSH/Sudo (perm deny)**
- Problema: Acesso negado por falta de chave ou sudo.
- Solução: Configurar ssh-copy-id para o usuário alvo e validar sudo sem senha ou com -K.

**Desafio 2: apt lock / cache desatualizado**
- Problema: Execução falha por lock do apt ou cache antigo.
- Solução: Tarefa inicial de update_cache e aguardar desbloqueio (ou checar processos apt/dpkg).

**Desafio 3: Python ausente no host gerenciado**
- Problema: Ansible não encontra python3 no destino.
- Solução: Garantir python3 instalado ou apontar ansible_python_interpreter correto no inventário.

## ⚡ Como Reproduzir

### Preparar Ambiente
```bash
sudo apt update && sudo apt install ansible
ssh-keygen -t ed25519
ssh-copy-id osboxes@192.168.15.5
```

### Executar
```bash
ansible -i hosts meus_clientes -m ping
ansible-playbook -i hosts instalar_programas.yml -K
```

---

<div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>
