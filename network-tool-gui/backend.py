import subprocess
import platform

def run_command(command):
    """Executa um comando no sistema e retorna a saída."""
    try:
        # subprocess.run é a forma moderna e recomendada de executar comandos externos.
        result = subprocess.run(
            command,
            capture_output=True,  # Captura a saída padrão (stdout) e os erros (stderr).
            text=True,            # Decodifica a saída e os erros como texto (usando o encoding padrão do sistema).
            check=True,           # Lança uma exceção (CalledProcessError) se o comando retornar um código de erro.
            timeout=30            # Define um tempo limite de 30 segundos para a execução do comando.
        )
        # Se o comando for bem-sucedido, retorna a saída padrão.
        return result.stdout
    except FileNotFoundError:
        # Ocorre se o comando (ex: 'ping') não for encontrado no PATH do sistema.
        return f"Erro: Comando '{command[0]}' não encontrado. Verifique se está instalado."
    except subprocess.CalledProcessError as e:
        # Ocorre quando 'check=True' e o comando retorna um erro.
        return f"Erro ao executar o comando:\n{e.stderr}"
    except subprocess.TimeoutExpired:
        # Ocorre se o comando levar mais de 30 segundos para terminar.
        return "Erro: O comando demorou muito para responder (timeout)."

def run_ping(host):
    """Prepara e executa o comando 'ping' de forma compatível com o sistema operacional."""
    # O parâmetro para definir o número de pings é '-n' no Windows e '-c' em Linux/macOS.
    # platform.system() retorna o nome do SO (ex: 'Windows', 'Linux').
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Monta a lista de argumentos para o comando.
    command = ['ping', param, '4', host]
    return run_command(command)

def run_traceroute(host):
    """Prepara e executa o comando 'traceroute' de forma compatível com o sistema operacional."""
    # O nome do comando é 'tracert' no Windows e 'traceroute' em Linux/macOS.
    command = 'tracert' if platform.system().lower() == 'windows' else 'traceroute'
    return run_command([command, host])

def run_nslookup(host):
    """Executa o nslookup e filtra a saída para retornar apenas as informações relevantes."""
    # Executa o comando nslookup.
    raw_output = run_command(['nslookup', host])

    # Se o comando retornou um erro, repassa o erro.
    if raw_output.startswith("Erro:"):
        return raw_output

    clean_lines = []
    # Processa cada linha da saída bruta para limpar informações desnecessárias.
    for line in raw_output.splitlines():
        # Converte a linha para minúsculas para uma comparação sem distinção de maiúsculas/minúsculas.
        # Mantém apenas as linhas que contêm as informações de nome e endereço.
        if line.lower().startswith('name:') or line.lower().startswith('address:'):
            # Adiciona a linha limpa (sem espaços extras no início/fim) à nossa lista.
            clean_lines.append(line.strip())

    # Se, após a filtragem, não sobrar nenhuma linha, retorna uma mensagem padrão.
    if not clean_lines:
        return "Nenhuma resposta de DNS válida encontrada."

    # Junta as linhas limpas em uma única string, separadas por quebras de linha.
    return "\n".join(clean_lines)