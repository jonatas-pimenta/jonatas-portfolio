import paramiko
import time

# --- Variáveis de Conexão ---
# O alvo do SSH é o seu próprio notebook (localhost).
# O Paramiko usará a chave.
HOST = 'localhost'
USUARIO = 'lion' # Seu nome de usuário do Linux
PORTA_SSH = 22

# --- Comando que será executado *dentro* do roteador FRR ---
# Este comando tem 3 partes:
# 1. docker exec -it: Entra no container de forma interativa.
# 2. frrouting-frr-1: O nome do roteador (que vamos ligar no GNS3).
# 3. vtysh -c 'show version': Entra no shell de roteamento e roda um comando.

COMANDO_VTYS = "docker exec -it kind_bohr vtysh -c 'show version'"

def run_command_via_ssh(host, port, user, command):
    """Conecta ao host via SSH e executa um comando."""
    
    # 1. Inicializar o cliente SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 2. Conectar ao localhost (usando a chave SSH)
        client.connect(hostname=host, port=port, username=user)
        print(f"--- Conectado com sucesso a {user}@{host} ---\n")
        
        # 3. Executar o comando no terminal do notebook
        # stdin: entrada, stdout: saída, stderr: erros
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)

        # 4. Ler a saída (Stdout)
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')

        if errors:
            print(f"--- ERRO ENCONTRADO ---\n{errors}")
        
        return output

    except Exception as e:
        return f"Falha na conexão SSH ou execução: {e}"
    finally:
        # 5. Fechar a conexão
        if client:
            client.close()

# --- Execução Principal ---
if __name__ == "__main__":
    print(f"Tentando executar: {COMANDO_VTYS}")
    
    # OBSERVAÇÃO CRÍTICA: Você precisa ligar o roteador no GNS3 antes de rodar este script!
    resultado = run_command_via_ssh(HOST, PORTA_SSH, USUARIO, COMANDO_VTYS)
    
    print("\n--- Resultado do Roteador ---")
    print(resultado)