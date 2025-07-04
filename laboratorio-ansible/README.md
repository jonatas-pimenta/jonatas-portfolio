# Laboratório de Automação com Ansible para Configuração de Servidores

### Resumo do Projeto
Este projeto demonstra a aplicação prática de automação e Infraestrutura como Código (IaC) utilizando Ansible. Foi criado um laboratório virtual com dois servidores Ubuntu, onde um "Nó de Controle" automatiza a instalação e configuração de um ambiente web em um "Nó Gerenciado", de forma padronizada e replicável.

---

### Apresentação do Cenário
Em um ambiente de TI, a necessidade de configurar novos servidores de forma rápida e consistente é constante. Realizar esse processo manualmente é demorado e suscetível a erros. Este projeto aborda esse desafio, utilizando Ansible para automatizar todo o fluxo de configuração inicial de um servidor.

### Arquitetura Visual
A infraestrutura do laboratório foi montada no VirtualBox, simulando uma rede simples com dois componentes principais, conforme o diagrama abaixo:

![Diagrama da Arquitetura do Laboratório Ansible](diagrama-arquitetura.png)

* **Nó de Controle (Servidor):** A máquina com IP `192.168.15.13`, responsável por armazenar o playbook e executar os comandos de automação.
* **Nó Gerenciado (Cliente):** A máquina alvo com IP `192.168.15.5`, que é configurada remotamente via SSH.

---

### Componentes da Solução

A automação é orquestrada por dois arquivos principais: o Inventário, que mapeia a infraestrutura, e o Playbook, que descreve as tarefas a serem executadas.

<details>
<summary><strong>📄 Playbook (`instalar_programas.yml`)</strong></summary>

```yaml
---
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
        enabled: yes
        state: started
