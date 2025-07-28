# Network Tool

Uma ferramenta de rede com interface gráfica desenvolvida em Python e Tkinter. Projetada para ser uma solução completa e amigável para tarefas comuns de diagnóstico e segurança de rede.

## Funcionalidades

- **Diagnóstico de Rede:**
  - **Ping:** Verifica a conectividade e a latência com um host.
  - **Traceroute:** Mapeia a rota que os pacotes levam até um host de destino.
  - **NSLookup:** Realiza consultas DNS com saída limpa e filtrada, mostrando apenas as informações essenciais.
  - **Salvar Resultados:** Permite exportar a saída completa do diagnóstico para um arquivo de texto, com data e hora da geração automaticamente adicionadas.

- **Scanner de Portas TCP:**
  - Escaneia portas específicas ou intervalos de portas em um host (ex: `80, 443, 1000-2000`).
  - Utiliza multithreading para um escaneamento rápido e eficiente.
  - Realiza "Banner Grabbing" para tentar identificar o serviço rodando em portas abertas.
  - **Barra de Progresso:** Fornece feedback visual em tempo real do andamento do escaneamento.
  - **Salvar Resultados:** Permite exportar a lista de portas abertas, com sugestão de nome de arquivo e conteúdo contendo data e hora.

- **Interface Gráfica e Experiência do Usuário:**
  - Organizada em abas para uma navegação clara entre as funcionalidades.
  - Executa tarefas de rede em threads separadas para garantir que a interface do usuário não congele durante as operações.
  - **Validação de Entrada:** Verifica se os dados inseridos (host, portas) são válidos antes de iniciar as tarefas.
  - **Feedback de Erro:** Exibe mensagens de erro claras e informativas usando pop-ups.
  - **Estilo Moderno:** Utiliza temas do `ttk` para uma aparência mais agradável e profissional.

## Screenshot

<p align="center">
  <img src="screenshot_diagnostico.png" width="48%">
  &nbsp;
  <img src="screenshot_scanner.png" width="48%">
</p>

## Requisitos

- Python 3.6 ou superior
- Tkinter (geralmente já vem instalado com o Python em sistemas Linux e Windows)

## Instalação e Uso

Siga os passos abaixo para executar a aplicação:

1.  **Clone o repositório (após subi-lo para o GitHub):**
    ```bash
    git clone https://github.com/seu-usuario/network-tool.git
    ```

2.  **Navegue até o diretório do projeto:**
    ```bash
    cd network-tool
    ```

3.  **Execute a aplicação:**
    ```bash
    python app.py
    ```

## Estrutura do Projeto

- `app.py`: O ponto de entrada da aplicação. Contém todo o código da interface gráfica (Tkinter) e a lógica para orquestrar as tarefas.
- `backend.py`: Módulo responsável por executar os comandos de diagnóstico (`ping`, `traceroute`, `nslookup`) usando o `subprocess`.
- `scanner.py`: Módulo que contém toda a lógica para o escaneamento de portas TCP, incluindo a análise de portas e o banner grabbing.