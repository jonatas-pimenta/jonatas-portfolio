#!/bin/bash

# -----------------------------------------------------------------------------
# Script para desativar o KVM e permitir a execução do VirtualBox
# Pede permissão de administrador (sudo) se não for executado como tal.
# -----------------------------------------------------------------------------

# 1. Verifica se o script está sendo executado como root (com sudo)
if [ "$EUID" -ne 0 ]; then
  echo "Permissão de administrador necessária. Executando novamente com sudo..."
  # Executa o script novamente com sudo, passando os mesmos argumentos
  exec sudo "$0" "$@"
  exit
fi

echo "Verificando módulos KVM para desativar..."

# 2. Detecta a CPU e desativa o módulo KVM correspondente
if lsmod | grep -q "kvm_intel"; then
  echo "-> CPU Intel detectada. Desativando 'kvm_intel'..."
  modprobe -r kvm_intel
elif lsmod | grep -q "kvm_amd"; then
  echo "-> CPU AMD detectada. Desativando 'kvm_amd'..."
  modprobe -r kvm_amd
else
  echo "-> Nenhum módulo KVM específico (Intel/AMD) encontrado em uso."
fi

# 3. Desativa o módulo KVM principal, se estiver ativo
if lsmod | grep -q "kvm"; then
  echo "-> Desativando módulo principal 'kvm'..."
  modprobe -r kvm
fi

echo ""
echo "✅ Pronto! Os módulos KVM foram desativados."
echo "Você já pode tentar iniciar sua máquina virtual no VirtualBox."