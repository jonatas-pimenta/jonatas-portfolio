# 🏢 Laboratório de Rede Corporativa

<div align="center">

![Cisco](https://img.shields.io/badge/Cisco-Packet_Tracer-blue.svg)
![VLANs](https://img.shields.io/badge/VLANs-6_Departamentos-green.svg)
![Security](https://img.shields.io/badge/Security-ACL_+_NAT-red.svg)
![Enterprise](https://img.shields.io/badge/Enterprise-Network-orange.svg)

**Infraestrutura de rede corporativa segmentada com Cisco Packet Tracer**

[🚀 Como Usar](#-como-executar) • [🏗️ Arquitetura](#-arquitetura-da-rede) • [💻 Tecnologias](#-tecnologias-demonstradas) • [💼 Para Recrutadores](./PARA_RECRUTADORES.md)

</div>

---

## 📋 Sobre o Projeto

Implementação completa de uma infraestrutura de rede corporativa segmentada, demonstrando boas práticas de segmentação departamental, políticas de segurança e conectividade externa em ambiente empresarial real.

---

## 🛠️ Tecnologias Utilizadas

![Cisco](https://img.shields.io/badge/Cisco-Packet_Tracer_8.2+-blue?logo=cisco)
![VLANs](https://img.shields.io/badge/VLANs-802.1Q_Trunking-green)
![DHCP](https://img.shields.io/badge/DHCP-Centralized_Server-yellow)
![ACL](https://img.shields.io/badge/ACL-Security_Policies-red)

---

## 💼 Funcionalidades

### 🏗️ **Segmentação de Rede**
- **🏢 6 VLANs Departamentais** - Isolamento completo de tráfego
- **🔀 Router-on-a-Stick** - Roteamento inter-VLAN eficiente
- **📊 DHCP Centralizado** - 6 pools com DHCP Relay configurado
- **🌐 WAN Simulada** - Conectividade externa com NAT Overload

### 🛡️ **Políticas de Segurança**
- **🚫 ACL Restritiva** - Departamento Produção bloqueado da internet
- **🔒 NAT Seletivo** - Acesso controlado à WAN por departamento
- **🔄 Spanning Tree** - Prevenção de loops de switching
- **🎯 Trunking 802.1Q** - Transporte seguro de VLANs

### ⚙️ **Configurações Avançadas**
- **📡 DHCP Relay (ip helper-address)** - Centralização de serviços
- **🌐 Sub-interfaces** - 6 gateways departamentais
- **🔐 Access Lists** - Políticas granulares de acesso

---

## 🏗️ Arquitetura da Rede

<p align="center">
  <img src="print_topologia.png" alt="Topologia da Rede Corporativa" width="75%">
</p>

### 🏢 **Segmentação Departamental por VLANs**

| Departamento | VLAN | Rede              | Gateway         | Dispositivos | Status Internet |
|--------------|------|-------------------|-----------------|--------------|-----------------|
| 🏛️ RH        | 10   | 192.168.10.0/24   | 192.168.10.1    | 5 PCs        | ✅ Permitido   |
| 💰 Vendas    | 20   | 192.168.20.0/24   | 192.168.20.1    | 5 PCs        | ✅ Permitido   |
| 🏭 Produção  | 30   | 192.168.30.0/24   | 192.168.30.1    | 14 PCs       | ❌ **Bloqueado** |
| 💼 Financeiro| 40   | 192.168.40.0/24   | 192.168.40.1    | 3 PCs        | ✅ Permitido   |
| 💻 TI (MGMT) | 99   | 192.168.99.0/24   | 192.168.99.1    | 2 PCs        | ✅ Permitido   |
| 👔 Diretoria | 100  | 192.168.100.0/24  | 192.168.100.1   | 1 PC         | ✅ Permitido   |

### 🔧 **Características Técnicas**
- **🖥️ DHCP Centralizado:** Servidor na VLAN 99 (192.168.99.100)
- **🔀 Router-on-a-Stick:** 6 sub-interfaces com 802.1Q
- **🛡️ Política de Segurança:** ACL específica para VLAN 30
- **🌐 NAT Inteligente:** Apenas departamentos autorizados

---

## 💻 Tecnologias Demonstradas

- **🏷️ VLANs e Trunking (802.1Q)** - Segmentação lógica avançada
- **🔀 Router-on-a-Stick** - Roteamento inter-VLAN otimizado  
- **📡 DHCP com Relay** - Centralização eficiente de serviços
- **🛡️ Access Control Lists (ACLs)** - Segurança granular
- **🌐 NAT Overload (PAT)** - Tradução inteligente para internet
- **🔄 Spanning Tree Protocol** - Prevenção de loops críticos

---

## 📋 Pré-requisitos

| Ferramenta          | Versão Mínima       |
|---------------------|---------------------|
| 🖥️ Cisco Packet Tracer | 8.2.2+          |
| 💻 Sistema Operacional  | Windows/Linux/macOS |

---

## 🚀 Como Executar

1. **Clone o repositório:**
   ```bash
   git clone [seu-repo] && cd network-lab-corporativo
   ```

2. **Abra o projeto:**
   ```bash
   # Execute o arquivo no Cisco Packet Tracer
   rede_corporativa.pkt
   ```

3. **Teste a conectividade:**
   - 🎭 **Modo Simulação:** Visualize fluxo de pacotes em tempo real
   - 🏓 **Teste Ping:** Conectividade entre diferentes VLANs
   - 🛡️ **Verificação de Segurança:** VLAN 30 bloqueada da internet
   - 📊 **DHCP:** Atribuição automática de IPs por departamento

---

## 📁 Estrutura do Projeto

```
network-lab-corporativo/
├── rede_corporativa.pkt         # 🎯 Arquivo principal do Packet Tracer
├── print_topologia.png          # 📸 Diagrama visual da topologia
├── configuracoes/               # ⚙️ Configurações dos dispositivos
│   ├── roteador_casa_config.txt    # Router-on-a-Stick principal
│   ├── roteador_internet_config.txt # Gateway WAN
│   ├── switch0_config.txt          # Switch com VLANs departamentais
│   └── switch1_config.txt          # Switch secundário
└── README.md                    # 📖 Documentação principal
```

---

## 🎯 Demonstração Técnica

<details>
<summary><strong>🔧 Configuração do Router-on-a-Stick (Clique para expandir)</strong></summary>

```cisco
! Interface principal
interface GigabitEthernet0/0
 no shutdown

! Sub-interfaces por departamento
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 ip helper-address 192.168.99.100  ! DHCP Relay

interface GigabitEthernet0/0.30
 encapsulation dot1Q 30
 ip address 192.168.30.1 255.255.255.0
 ip helper-address 192.168.99.100

! 🛡️ ACL - Bloquear Produção da internet
access-list 101 deny ip 192.168.30.0 0.0.0.255 any
access-list 101 permit ip any any

! 🌐 NAT - Apenas departamentos autorizados
access-list 1 permit 192.168.10.0 0.0.0.255  ! RH
access-list 1 permit 192.168.20.0 0.0.0.255  ! Vendas
access-list 1 permit 192.168.40.0 0.0.0.255  ! Financeiro
access-list 1 permit 192.168.99.0 0.0.0.255  ! TI
access-list 1 permit 192.168.100.0 0.0.0.255 ! Diretoria
! ❌ VLAN 30 (Produção) intencionalmente omitida

ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

</details>

---

## 🔗 Conecte-se Comigo

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)](https://github.com/jonatas-pimenta)

</div>

---

## 🔗 Conecte-se Comigo

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=flat)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)](https://github.com/jonatas-pimenta)

</div>
