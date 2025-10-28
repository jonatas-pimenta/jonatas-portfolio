# -*- coding: utf-8 -*-

from scapy.all import sniff, IP, ICMP, TCP, UDP

# Esta função será chamada para cada pacote capturado
def processar_pacote(pacote):
    """
    Analisa e imprime informações sobre o pacote capturado.
    """
    # Verifica se o pacote tem a camada de IP
    if pacote.haslayer(IP):
        ip_origem = pacote[IP].src
        ip_destino = pacote[IP].dst
        
        protocolo_nome = "Outro" # Valor padrão
        
        # Identifica o protocolo da camada de transporte
        if pacote.haslayer(ICMP):
            protocolo_nome = "ICMP"
        elif pacote.haslayer(TCP):
            protocolo_nome = "TCP"
        elif pacote.haslayer(UDP):
            protocolo_nome = "UDP"

        print(f"Pacote IP Capturado: {ip_origem} -> {ip_destino} | Protocolo: {protocolo_nome}")


print(">>> Iniciando o sniffer de pacotes... Pressione CTRL+C para parar. <<<")

# Inicia a captura de pacotes.
# O filtro "ip" garante que capturaremos apenas pacotes que contenham uma camada IP.
# prn=processar_pacote indica que a nossa função será executada para cada pacote.
# store=0 diz para não guardar os pacotes na memória, economizando recursos.
sniff(filter="ip", prn=processar_pacote, store=0)

print("\n>>> Sniffer parado. <<<")