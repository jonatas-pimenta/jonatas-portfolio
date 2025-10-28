#!/bin/bash

# backup_engine.sh - Engine de backup integrado com GUI Python
set -euo pipefail

# Configurações
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="$SCRIPT_DIR/backup_history.log"
readonly LOCK_FILE="$SCRIPT_DIR/backup.lock"
readonly TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
readonly START_TIME=$(date +%s)

# Função para verificar dependências
check_dependencies() {
    command -v rsync >/dev/null 2>&1 || {
        echo "ERRO: rsync não está instalado"
        exit 1
    }
}

# Função para verificar espaço em disco
check_disk_space() {
    local source_size=$(du -sb "$SOURCE" 2>/dev/null | cut -f1 || echo 0)
    local dest_available=$(df -B1 "$DEST" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0)
    
    if [ "$source_size" -gt "$dest_available" ]; then
        echo "AVISO: Espaço pode ser insuficiente no destino"
        echo "- Tamanho origem: $(numfmt --to=iec "$source_size" 2>/dev/null || echo "N/A")"
        echo "- Espaço disponível: $(numfmt --to=iec "$dest_available" 2>/dev/null || echo "N/A")"
    fi
}

# Criar arquivo de log com permissões corretas se não existir
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
fi

# Evitar execuções concorrentes
if [ -f "$LOCK_FILE" ]; then
    echo "ERRO: Backup já em andamento! Arquivo de lock: $LOCK_FILE"
    exit 1
fi

# Configurar trap para limpeza
trap 'rm -f "$LOCK_FILE"; exit' EXIT INT TERM
echo "$$ $TIMESTAMP" > "$LOCK_FILE"

# Funções auxiliares
log_and_display() {
    local message="$1"
    echo "$message"
    echo "$TIMESTAMP - $message" >> "$LOG_FILE"
}

get_size() {
    if [ -f "$1" ]; then
        du -h "$1" 2>/dev/null | awk '{print $1}'
    elif [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | awk '{print $1}'
    else
        echo "N/A"
    fi
}

format_time() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local secs=$((seconds % 60))
    echo "${minutes}m ${secs}s"
}

# Verificação de argumentos
if [ "$#" -ne 2 ]; then
    echo "ERRO: Uso correto: $0 <origem> <destino>"
    exit 1
fi

SOURCE="$1"
DEST="$2"

# Executar verificações iniciais
check_dependencies

# Verificações de entrada
echo "Verificando parâmetros de entrada..."

if [ ! -e "$SOURCE" ]; then
    echo "ERRO: Item de origem '$SOURCE' não existe!"
    exit 1
fi

if [ ! -d "$DEST" ]; then
    echo "Criando diretório de destino: $DEST"
    mkdir -p "$DEST" || {
        echo "ERRO: Não foi possível criar diretório de destino"
        exit 1
    }
fi

# Verificar espaço em disco
check_disk_space

# Informações do backup
echo "Configurações do backup:"
echo "- Origem: $SOURCE"
echo "- Destino: $DEST"
echo "- Tipo: $(if [ -f "$SOURCE" ]; then echo "Arquivo"; else echo "Diretório"; fi)"
echo "- Tamanho origem: $(get_size "$SOURCE")"
echo "- Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')"
echo ""

# Execução do backup com rsync
echo "Iniciando processo de cópia..."
echo "Comando: rsync -avh --progress --delete --stats"

# Configurar opções do rsync
RSYNC_OPTIONS=(
    -avh
    --progress
    --delete
    --stats
    --human-readable
    --exclude='*.tmp'
    --exclude='*.log'
    --exclude='*.swp'
    --exclude='.DS_Store'
    --exclude='Thumbs.db'
    --exclude='*.~lock*'
)

# Executar rsync e capturar saída
rsync "${RSYNC_OPTIONS[@]}" "$SOURCE" "$DEST/" 2>&1

# Capturar código de saída
BACKUP_STATUS=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "Processo finalizado!"
echo "- Código de saída: $BACKUP_STATUS"
echo "- Tempo total: $(format_time $DURATION)"

# Verificar resultado
if [ $BACKUP_STATUS -eq 0 ]; then
    DEST_ITEM="$DEST/$(basename "$SOURCE")"
    FINAL_SIZE=$(get_size "$DEST_ITEM")
    echo "- Status: SUCESSO"
    echo "- Tamanho final: $FINAL_SIZE"
    echo "- Local: $DEST_ITEM"
    
    # Log detalhado no arquivo
    {
        echo ""
        echo "========================================="
        echo "BACKUP CONCLUÍDO COM SUCESSO"
        echo "Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')"
        echo "Origem: $SOURCE ($(get_size "$SOURCE"))"
        echo "Destino: $DEST_ITEM ($(get_size "$DEST_ITEM"))"
        echo "Duração: $(format_time $DURATION)"
        echo "========================================="
        echo ""
    } >> "$LOG_FILE"
    
else
    echo "- Status: FALHA"
    echo "- Código de erro: $BACKUP_STATUS"
    
    # Log de erro no arquivo
    {
        echo ""
        echo "========================================="
        echo "BACKUP FALHOU"
        echo "Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')"
        echo "Origem: $SOURCE"
        echo "Destino: $DEST"
        echo "Código de erro: $BACKUP_STATUS"
        echo "Duração: $(format_time $DURATION)"
        echo "========================================="
        echo ""
    } >> "$LOG_FILE"
fi

# Limpeza do arquivo de lock será feita pelo trap
exit $BACKUP_STATUS