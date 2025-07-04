# Laboratório de Automação com Ansible

Um projeto para demonstrar a automação da configuração de servidores Ubuntu usando Ansible e os princípios de Infraestrutura como Código (IaC). O laboratório consiste em um "Nó de Controle" que provisiona um ambiente web em um "Nó Gerenciado" de forma padronizada e replicável.

## Funcionalidades

- **Atualização de Pacotes:** Garante que o cache de pacotes `apt` esteja sempre atualizado antes de qualquer instalação.
- **Instalação de Ferramentas:** Instala um conjunto de pacotes essenciais para administração e diagnóstico, incluindo `htop`, `net-tools`, `curl` e `tmux`.
- **Provisionamento de Servidor Web:** Instala, habilita e inicia o servidor web Apache2, deixando-o pronto para servir aplicações.
- **Idempotência:** O playbook pode ser executado várias vezes, garantindo sempre o mesmo estado final sem causar erros.

## Arquitetura do Laboratório

A infraestrutura foi montada no VirtualBox, simulando uma rede simples com um nó de controle e um nó gerenciado.

<p align="center">
  <img src="diagrama-arquitetura.png" alt="Diagrama da Arquitetura do Laboratório Ansible" width="70%">
</p>

* **Nó de Controle (Servidor):** A máquina com IP `192.168.15.13`, responsável por armazenar o playbook e executar os comandos de automação.
* **Nó Gerenciado (Cliente):** A máquina alvo com IP `192.168.15.5`, que é configurada remotamente via SSH.

## Requisitos do Ambiente

Para executar esta automação, seu ambiente precisa atender aos seguintes pré-requisitos:

### Nó de Controle
A máquina de onde você executará os comandos do Ansible.
- **Sistema Operacional:** Linux ou macOS.
  - *Para usuários de Windows, é necessário usar o WSL (Subsistema do Windows para Linux).*
- **Software:** Ansible e Python (versão 3.8 ou superior).

### Nós Gerenciados
Os servidores que serão configurados pelo Ansible (neste projeto, um servidor Ubuntu).
- **Conectividade:** Acesso via SSH a partir do Nó de Controle.
- **Software:** Um interpretador Python (versão 2.7 ou 3.5+) para executar as tarefas do Ansible.

## Como Usar

1.  **Clone o repositório (exemplo):**
    ```bash
    git clone https://github.com/seu-usuario/laboratorio-ansible.git
    cd laboratorio-ansible
    ```

2.  **Configure o Inventário:**
    Ajuste o arquivo `inventario.ini` com o endereço IP e o usuário corretos para o seu nó gerenciado.

3.  **Teste a Conexão:**
    Verifique se o Nó de Controle consegue se conectar ao Nó Gerenciado.
    ```bash
    ansible meus_clientes -m ping
    ```
    A saída esperada é uma resposta `SUCCESS` em verde.

4.  **Execute o Playbook:**
    Aplique a configuração no nó gerenciado.
    ```bash
    ansible-playbook instalar_programas.yml
    ```

## Estrutura do Projeto

- `instalar_programas.yml`: O Playbook do Ansible que descreve todas as tarefas a serem executadas no nó gerenciado.
- `inventario.ini`: O arquivo de inventário que define os hosts e grupos de hosts que o Ansible irá gerenciar.
- `README.md`: Este arquivo.
- `diagrama-arquitetura.png`: Imagem do diagrama da arquitetura.

---
<details>
<summary><strong>Código do Playbook (`instalar_programas.yml`)</strong></summary>

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
