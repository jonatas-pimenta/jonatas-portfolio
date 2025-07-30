# Guia de Inicialização Rápida

## Passos para executar o laboratório:

### 1. Verificar Pré-requisitos
- [ ] Cisco Packet Tracer 8.2.2+ instalado
- [ ] Sistema operacional compatível (Windows/Linux/macOS)

### 2. Carregar o Projeto
1. Abrir o Cisco Packet Tracer
2. Ir em `File > Open`
3. Selecionar o arquivo `rede_corporativa.pkt`

### 3. Explorar a Topologia
- **Matriz:** Equipamentos principais na parte esquerda
- **Filial:** Equipamentos na parte direita
- **Conexão WAN:** Link serial no centro

### 4. Testes Básicos de Conectividade

#### Teste 1: Comunicação Intra-VLAN (Dentro do mesmo departamento)
```
PC-RH1> ping 192.168.10.5        # Teste dentro da VLAN 10 (RH)
PC-Vendas1> ping 192.168.20.3    # Teste dentro da VLAN 20 (Vendas)
PC-Producao1> ping 192.168.30.10 # Teste dentro da VLAN 30 (Produção)
```

#### Teste 2: Comunicação Inter-VLAN (Entre departamentos)
```
PC-RH1> ping 192.168.20.1        # RH para gateway de Vendas
PC-Vendas1> ping 192.168.40.1    # Vendas para gateway do Financeiro
PC-TI1> ping 192.168.100.1       # TI para gateway da Diretoria
```

#### Teste 3: Teste de DHCP (Renovação automática de IP)
```
PC-RH1> ipconfig /release
PC-RH1> ipconfig /renew
PC-RH1> ipconfig               # Verificar se recebeu IP do pool correto
```

#### Teste 4: Política de Segurança - Acesso à Internet
```
# Departamentos com acesso à internet (deve funcionar)
PC-RH1> ping 8.8.8.8
PC-Vendas1> ping 8.8.8.8
PC-Financeiro1> ping 8.8.8.8
PC-Diretoria1> ping 8.8.8.8

# Departamento de Produção (deve FALHAR - bloqueado por ACL)
PC-Producao1> ping 8.8.8.8      # Este ping deve falhar
```

#### Teste 5: Servidor Web Externo
```
PC-RH1> ping 200.200.200.1      # Gateway WAN
PC-Vendas1> http://8.8.8.8      # Acesso via browser (se disponível)
```

### 5. Modo de Simulação
1. Clicar no ícone "Simulation" no canto inferior direito
2. Selecionar tipos de pacotes (ICMP, DHCP, etc.)
3. Executar comandos ping nos PCs
4. Observar o caminho dos pacotes

### 6. Verificar Configurações
- As configurações estão na pasta `configuracoes/`
- Cada arquivo contém a configuração completa do respectivo dispositivo
- Use como referência para estudo e implementação

### 7. Troubleshooting Comum
- **Não há conectividade:** Verificar se as interfaces estão `no shutdown`
- **DHCP não funciona:** Verificar configuração do ip helper-address
- **ACLs bloqueando:** Revisar as regras de access-list

### 8. Funcionalidades Avançadas para Testar
- [ ] Funcionamento do DHCP com 6 pools diferentes
- [ ] DHCP Relay (ip helper-address) funcionando em todas as VLANs
- [ ] Roteamento inter-VLAN entre os 6 departamentos
- [ ] Política de segurança: VLAN 30 (Produção) bloqueada da internet
- [ ] NAT Overload funcionando para VLANs permitidas
- [ ] Conectividade WAN e acesso ao servidor externo (8.8.8.8)
- [ ] Trunk links transportando tráfego de múltiplas VLANs
- [ ] Isolamento correto entre departamentos via VLANs

### 9. Análise dos Pools DHCP por Departamento
Verificar se cada departamento está recebendo IPs do pool correto:
- **RH (VLAN 10):** 192.168.10.2 - 192.168.10.254
- **Vendas (VLAN 20):** 192.168.20.2 - 192.168.20.254  
- **Produção (VLAN 30):** 192.168.30.2 - 192.168.30.254
- **Financeiro (VLAN 40):** 192.168.40.2 - 192.168.40.254
- **TI (VLAN 99):** 192.168.99.2 - 192.168.99.254
- **Diretoria (VLAN 100):** 192.168.100.2 - 192.168.100.254
