# 🌐 Laboratório de Roteamento BGP Inter-AS

<div align="center">

![Cisco](https://img.shields.io/badge/Cisco-1BA0D7?style=flat&logo=cisco&logoColor=white)
![BGP](https://img.shields.io/badge/BGP-6_Sistemas_Autônomos-orange?style=flat&logo=cisco&logoColor=white)
![Troubleshooting](https://img.shields.io/badge/Troubleshooting-Adaptação_Técnica-red?style=flat&logo=shield&logoColor=white)
![Packet Tracer](https://img.shields.io/badge/Packet_Tracer-8.2+-blue?style=flat&logo=cisco&logoColor=white)

**Simulação de interconexão entre múltiplos Sistemas Autônomos (AS) utilizando o protocolo BGP**

[🚀 Execução](#-como-reproduzir) • [💼 Funcionalidades](#-funcionalidades-implementadas) • [🎬 Demo](#-demonstração-em-vídeo) • [💼 Para Recrutadores](#-valor-para-recrutadores)

</div>

---

## 📋 Descrição do Projeto

Este laboratório avançado de redes, implementado no Cisco Packet Tracer, simula a interconexão de redes complexas através do **BGP (Border Gateway Protocol)**. O plano original replicava um cenário corporativo real com dois grandes Sistemas Autônomos (AS 100 e AS 200), o que exigiria o uso de BGP tanto externo (eBGP) quanto interno (iBGP) para a comunicação completa.

Durante a implementação, foi identificado que a versão utilizada do Cisco Packet Tracer não oferece suporte a sessões iBGP. Diante deste desafio técnico, o projeto foi estrategicamente adaptado: a rede foi re-arquitetada para um modelo "um AS por roteador", utilizando exclusivamente eBGP. Esta adaptação não apenas viabilizou o laboratório, mas transformou-o em um estudo de caso sobre resolução de problemas e flexibilidade em engenharia de redes.

---

## 🎬 Demonstração em Vídeo

<div align="center">
<a href="#" target="_blank">
  <img src="https://img.shields.io/badge/Assistir_Vídeo_Demo-red?style=for-the-badge&logo=youtube&logoColor=white" alt="Assistir vídeo de demonstração">
</a>

<p style="margin-top: 12px;">
💡 <em>Veja o BGP em ação — a prova de que a rede convergiu e tem conectividade total.</em>
</p>

</div>

**O que você verá no vídeo:**
- A topologia completa do laboratório explicada
- A verificação das sessões BGP estabelecidas (`show ip bgp summary`)
- Análise da tabela de roteamento do R1 (`show ip route`)
- Teste de conectividade ponta a ponta com `ping`
- Demonstração do fluxo de pacotes com o Modo Simulação

---

## 🏗️ Arquitetura do Laboratório

<p align="center">
  <img src="topologia-bgp-inter-as.png" width="75%" alt="Arquitetura do Laboratório BGP Inter-AS">
</p>

**Resumo da Arquitetura:**
- **6 Roteadores Cisco 2911**, cada um operando como um Sistema Autônomo (AS) independente.
- **7 Conexões Ponto a Ponto**, formando uma topologia com múltiplos caminhos.
- **Protocolo eBGP** utilizado em todas as conexões para troca de informações de roteamento.
- **Decisão de Arquitetura:** O plano inicial (AS 100 e AS 200 com iBGP) foi adaptado para um modelo de eBGP puro (um AS por roteador) como resposta a uma limitação técnica da ferramenta, demonstrando flexibilidade no design do projeto.

---

## 🚀 Resultado da Execução

<p align="center">
    <img src="resultado-show-ip-route.png" width="80%" alt="Resultado do comando show ip route no R1">
</p>

**Resultado demonstrado:**
- ✅ **Convergência Completa:** A tabela de roteamento do R1 contém rotas para todas as redes da topologia.
- ✅ **Rotas BGP Aprendidas:** Rotas para redes remotas (ex: `10.0.56.0/24`) estão presentes e marcadas com `B`.
- ✅ **Conectividade Ponta a Ponta:** Um `ping` do R1 para o R5 (o roteador mais distante) é bem-sucedido.

---

## 🚀 Implementação Atual

### Configuração BGP do R1 (AS 65001)
```cisco
router bgp 65001
 neighbor 10.0.12.2 remote-as 65002
 neighbor 10.0.13.3 remote-as 65003
 network 10.0.12.0 mask 255.255.255.0
 network 10.0.13.0 mask 255.255.255.0
 ```
 ---
 
 <div align="center">
 
Estudante de Redes de Computadores | Aprendizado contínuo através de projetos práticos 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jonatas--pimenta-black?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/jonatas-pimenta-9ab861288/)
[![GitHub](https://img.shields.io/badge/GitHub-Ver_Mais_Projetos-black?logo=github&style=for-the-badge)](https://github.com/jonatas-pimenta)

</div>