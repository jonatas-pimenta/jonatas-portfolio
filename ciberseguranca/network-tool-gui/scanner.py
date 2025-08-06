import socket
import threading
import queue

def _parse_ports(ports_str):
    """Analisa uma string de portas (ex: '80, 1-100, 443') em uma lista ordenada de inteiros."""
    # Usamos um 'set' para evitar portas duplicadas automaticamente.
    ports_to_scan = set()
    try:
        # Divide a string por vírgulas para lidar com múltiplos intervalos/portas.
        for p_range in ports_str.split(','):
            p_range = p_range.strip()
            if not p_range: continue
            # Se houver um hífen, trata-se de um intervalo.
            if '-' in p_range:
                start, end = map(int, p_range.split('-'))
                # Validação para garantir que as portas estão no intervalo válido (1-65535).
                if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
                    raise ValueError("Intervalo de portas inválido.")
                ports_to_scan.update(range(start, end + 1))
            else:
                # Trata-se de uma porta única.
                port_num = int(p_range)
                # Validação para a porta única.
                if not (1 <= port_num <= 65535):
                    raise ValueError("Número de porta inválido.")
                ports_to_scan.add(port_num)
        # Retorna uma lista ordenada de portas únicas.
        return sorted(list(ports_to_scan))
    except (ValueError, TypeError): # Captura erros de conversão (ex: 'abc') ou de formato.
        return None # Indica um erro de análise

def _scan_port(host_ip, port, results_queue):
    """Tenta conectar a uma porta. Se aberta, captura o banner e coloca o resultado na fila."""
    try:
        # 'with' garante que o socket será fechado automaticamente no final.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Define um timeout curto para a conexão. Essencial para scans rápidos.
            s.settimeout(0.5)
            # s.connect_ex() não lança uma exceção se a conexão falhar, em vez disso, retorna um código de erro.
            # Retorna 0 em caso de sucesso (porta aberta).
            if s.connect_ex((host_ip, port)) == 0:
                banner = "N/A"
                try:
                    # Tenta receber até 1024 bytes de dados (o "banner" do serviço).
                    banner_bytes = s.recv(1024)
                    # Decodifica os bytes para uma string de texto, ignorando erros de caracteres.
                    banner = banner_bytes.decode('utf-8', errors='ignore').strip()
                except (socket.timeout, ConnectionResetError):
                    # Se o serviço não enviar um banner a tempo (timeout) ou fechar a conexão, ignora.
                    pass
                # Coloca o resultado (porta, banner) na fila para a GUI processar.
                results_queue.put((port, banner))
    except (socket.error, socket.timeout):
        # Captura outros erros de socket que possam ocorrer.
        pass

def run_scan(host, ports_str, workers=100):
    """
    Função de preparação para o scan de portas.
    Valida o host e as portas, retornando o IP resolvido e a lista de portas.
    """
    try:
        # Resolve o nome do host (ex: 'google.com') para um endereço IP.
        target_ip = socket.gethostbyname(host)
    except socket.gaierror:
        return f"Erro: Hostname '{host}' não pôde ser resolvido."

    ports = _parse_ports(ports_str)
    if ports is None:
        return "Erro: Formato de porta inválido. Use números, vírgulas e hífens (ex: 80, 100-200)."

    # A lógica de threading e a criação da fila são gerenciadas pela GUI (app.py) para permitir
    # atualizações em tempo real (como a barra de progresso).
    return target_ip, ports