# 🏢 Network Lab Corporativo

<div align="center">

![Cisco](https://img.shields.io/badge/Cisco-1BA0D7?style=flat&logo=cisco&logoColor=white)
![VLANs](https://img.shields.io/badge/VLANs-6_Departamentos-green?style=flat&logo=cisco&logoColor=white)
![Security](https://img.shields.io/badge/Security-ACL_+_NAT-red?style=flat&logo=shield&logoColor=white)
![Packet Tracer](https://img.shields.io/badge/Packet_Tracer-8.2+-blue?style=flat&logo=cisco&logoColor=white)

**Infraestrutura de rede corporativa segmentada com políticas de segurança avançadas**

[🚀 Instalação](#-como-executar) • [💼 Funcionalidades](#-funcionalidades) • [🎯 Arquitetura](#-arquitetura-da-rede) • [💼 Para Recrutadores](#-valor-para-recrutadores)

</div>

---

## 📋 Descrição do Projeto

Este é um laboratório completo de rede corporativa implementado no Cisco Packet Tracer, demonstrando segmentação departamental através de VLANs, políticas de segurança granulares e conectividade externa controlada. O projeto simula um ambiente empresarial real com 6 departamentos isolados e regras de acesso específicas.

A rede implementa conceitos avançados como Router-on-a-Stick, DHCP centralizado com relay, ACLs restritivas e NAT seletivo, proporcionando uma base sólida para entender infraestruturas de rede corporativas modernas.

---

## 🏗️ Arquitetura da Rede

<p align="center">
  <img src="print_topologia.png" width="75%" alt="Topologia da Rede Corporativa no Packet Tracer">
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

**Características da Arquitetura:**
- **DHCP Centralizado:** Servidor na VLAN 99 (192.168.99.100)
- **Router-on-a-Stick:** 6 sub-interfaces com encapsulamento 802.1Q
- **Política de Segurança:** ACL específica bloqueando VLAN 30 da internet
- **NAT Seletivo:** Apenas departamentos autorizados acessam WAN

---

## 🚀 Habilidades Técnicas Aplicadas

**Redes e Switching**
- VLANs e Trunking 802.1Q para segmentação
- Spanning Tree Protocol para prevenção de loops
- Configuração de switches Cisco com VLANs
- Implementação de trunk links entre switches

**Roteamento e Conectividade**
- Router-on-a-Stick para roteamento inter-VLAN
- Sub-interfaces com encapsulamento dot1Q
- Roteamento estático para conectividade WAN
- DHCP Relay (ip helper-address) para centralização

**Segurança de Rede**
- Access Control Lists (ACLs) para controle de tráfego
- NAT Overload (PAT) com listas seletivas
- Políticas de segurança por departamento
- Isolamento de redes críticas (Produção)

---

## 💼 Funcionalidades

### 🏗️ Segmentação de Rede
- **6 VLANs Departamentais** - Isolamento completo de tráfego
- **Router-on-a-Stick** - Roteamento inter-VLAN eficiente
- **DHCP Centralizado** - 6 pools com DHCP Relay configurado
- **WAN Simulada** - Conectividade externa com NAT Overload

### 🛡️ Políticas de Segurança
- **ACL Restritiva** - Departamento Produção bloqueado da internet
- **NAT Seletivo** - Acesso controlado à WAN por departamento
- **Spanning Tree** - Prevenção de loops de switching
- **Trunking 802.1Q** - Transporte seguro de VLANs

### ⚙️ Configurações Avançadas
- **DHCP Relay** - Centralização de serviços de rede
- **Sub-interfaces** - 6 gateways departamentais
- **Access Lists** - Políticas granulares de acesso
- **Network Address Translation** - Conectividade externa controlada

---

## 📋 Pré-requisitos

- **Cisco Packet Tracer 8.2+** (testado em 8.2.2)
- **Sistema Operacional:** Windows/Linux/macOS
- **Conhecimento básico:** Conceitos de redes TCP/IP
- **Hardware:** 4GB RAM mínimo para execução fluida

---

## 🚀 Como Executar

### Instalação e Execução
```bash
# 1. Clone o repositório
git clone https://github.com/jonatas-pimenta/jonatas-portfolio.git
cd Infraestrutura/network-lab-corporativo

# 2. Abra no Packet Tracer
# Execute o arquivo: rede_corporativa.pkt
```

### Testes de Funcionalidade
1. **Modo Simulação** - Visualize fluxo de pacotes em tempo real
2. **Teste Ping** - Conectividade entre diferentes VLANs
3. **Verificação de Segurança** - VLAN 30 bloqueada da internet
4. **DHCP** - Atribuição automática de IPs por departamento
5. **Navegação Web** - Acesso externo para departamentos autorizados

---

## 📁 Estrutura do Projeto

```
network-lab-corporativo/
├── rede_corporativa.pkt         # Arquivo principal do Packet Tracer
├── print_topologia.png          # Diagrama visual da topologia
├── configuracoes/               # Configurações dos dispositivos
│   ├── roteador_casa_config.txt    # Router-on-a-Stick principal
│   ├── roteador_internet_config.txt # Gateway WAN
│   ├── switch0_config.txt          # Switch com VLANs departamentais
│   └── switch1_config.txt          # Switch secundário
└── README.md                    # Documentação principal
```

---

## 🔧 Demonstração Técnica

### Configuração do Router-on-a-Stick
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

! ACL - Bloquear Produção da internet
access-list 101 deny ip 192.168.30.0 0.0.0.255 any
access-list 101 permit ip any any

! NAT - Apenas departamentos autorizados
access-list 1 permit 192.168.10.0 0.0.0.255  ! RH
access-list 1 permit 192.168.20.0 0.0.0.255  ! Vendas
access-list 1 permit 192.168.40.0 0.0.0.255  ! Financeiro
access-list 1 permit 192.168.99.0 0.0.0.255  ! TI
access-list 1 permit 192.168.100.0 0.0.0.255 ! Diretoria
! VLAN 30 (Produção) intencionalmente omitida

ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

---

## 🔍 Conceitos Aplicados

### **Arquitetura de Redes Corporativas**
- Segmentação departamental com VLANs
- Hierarquia de rede em três camadas
- Redundância e tolerância a falhas
- Escalabilidade para crescimento futuro

### **Segurança de Rede Empresarial**
- Políticas de acesso por departamento
- Isolamento de redes críticas
- Controle granular de tráfego
- Prevenção de vazamento de dados

### **Administração de Rede**
- Centralização de serviços (DHCP)
- Padronização de configurações
- Monitoramento de tráfego
- Documentação técnica detalhada

---

## 💼 Valor para Recrutadores

### Competências Demonstradas
- **Cisco Networking** - Configuração avançada de equipamentos Cisco
- **VLANs e Switching** - Segmentação e otimização de tráfego
- **Roteamento Inter-VLAN** - Router-on-a-Stick e sub-interfaces
- **Segurança de Rede** - ACLs, NAT e políticas restritivas
- **DHCP Enterprise** - Relay e centralização de serviços
- **Troubleshooting** - Diagnóstico e resolução de problemas

### Aplicabilidade Profissional
- **Administração de Rede** - Gestão de infraestrutura corporativa
- **Segurança Corporativa** - Implementação de políticas de acesso
- **Design de Rede** - Arquitetura escalável e segura
- **Suporte Técnico** - Manutenção e otimização de redes
- **Consultoria** - Projetos de infraestrutura empresarial

### Casos de Uso Reais
- Segmentação de rede em empresas médias
- Isolamento de departamentos críticos
- Implementação de políticas de segurança
- Centralização de serviços de rede
- Preparação para certificações Cisco (CCNA)

---

## 🤝 Contato e Portfólio

<div align="center">

**Desenvolvido por [Jonatas Pimenta](https://github.com/jonatas-pimenta)**  
Estudante de Redes de Computadores | Buscando oportunidades de estágio em Tecnologia  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-blue?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

🎯 Este projeto demonstra conhecimentos avançados em redes Cisco e arquitetura de infraestrutura corporativa.

</div>