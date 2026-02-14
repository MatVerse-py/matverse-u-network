#!/usr/bin/env bash
set -euo pipefail

# MatVerse Network - WireGuard Key Generator
# Gera pares de chaves Curve25519 para cada nó

VERSION="1.0.0"
NODE_NAME=""
OUTPUT_DIR=""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat <<EOF
MatVerse Network - WireGuard Key Generator v${VERSION}

Uso:
    $0 --node=<nome> --output=<diretorio>

Opções:
    --node=<nome>         Nome do nó (ex: core, twin, tablet-1)
    --output=<diretorio>  Diretório de saída para as chaves
    --help                Mostrar esta ajuda

Exemplo:
    $0 --node=core --output=configs/core/
EOF
    exit 1
}

check_wireguard() {
    if ! command -v wg &> /dev/null; then
        log_error "WireGuard não encontrado. Instale com:"
        echo "  Ubuntu/Debian: sudo apt install wireguard"
        echo "  macOS: brew install wireguard-tools"
        exit 1
    fi
}

generate_keys() {
    log_info "Gerando par de chaves para nó: ${NODE_NAME}"
    
    # Criar diretório de saída se não existir
    mkdir -p "${OUTPUT_DIR}"
    
    # Gerar chave privada
    PRIVATE_KEY=$(wg genkey)
    
    # Derivar chave pública
    PUBLIC_KEY=$(echo "${PRIVATE_KEY}" | wg pubkey)
    
    # Salvar chaves
    echo "${PRIVATE_KEY}" > "${OUTPUT_DIR}/privatekey"
    echo "${PUBLIC_KEY}" > "${OUTPUT_DIR}/publickey"
    
    # Proteger chave privada
    chmod 600 "${OUTPUT_DIR}/privatekey"
    chmod 644 "${OUTPUT_DIR}/publickey"
    
    log_info "Chaves geradas e salvas em: ${OUTPUT_DIR}"
    echo
    echo "  Private Key: ${OUTPUT_DIR}/privatekey"
    echo "  Public Key:  ${OUTPUT_DIR}/publickey"
    echo
    echo "  Public Key (para configuração de peers):"
    echo "  ${PUBLIC_KEY}"
    echo
    
    # Criar arquivo de template de configuração
    create_config_template
}

create_config_template() {
    log_info "Criando template de configuração..."
    
    # Determinar IP baseado no nome do nó
    case "${NODE_NAME}" in
        core)
            IP="10.0.0.1"
            LISTEN_PORT="51820"
            ;;
        twin)
            IP="10.0.0.2"
            LISTEN_PORT=""
            ;;
        tablet-1)
            IP="10.0.0.3"
            LISTEN_PORT=""
            ;;
        tablet-2)
            IP="10.0.0.4"
            LISTEN_PORT=""
            ;;
        mobile)
            IP="10.0.0.5"
            LISTEN_PORT=""
            ;;
        *)
            IP="10.0.0.99"
            LISTEN_PORT=""
            ;;
    esac
    
    cat > "${OUTPUT_DIR}/wg0.conf.template" <<EOF
# MatVerse Network - WireGuard Configuration
# Node: ${NODE_NAME}
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

[Interface]
# Chave privada deste nó
PrivateKey = ${PRIVATE_KEY}

# Endereço IP na rede MatVerse
Address = ${IP}/24

EOF

    if [ -n "${LISTEN_PORT}" ]; then
        cat >> "${OUTPUT_DIR}/wg0.conf.template" <<EOF
# Porta de escuta (apenas para nós hub)
ListenPort = ${LISTEN_PORT}

EOF
    fi

    cat >> "${OUTPUT_DIR}/wg0.conf.template" <<EOF
# DNS (opcional)
# DNS = 10.0.0.1

# Scripts de inicialização/desligamento (opcional)
# PostUp = iptables -A FORWARD -i %i -j ACCEPT
# PostDown = iptables -D FORWARD -i %i -j ACCEPT

# ============================================
# PEERS
# ============================================
# Adicione aqui os peers (outros nós)
# Exemplo:
#
# [Peer]
# PublicKey = <PUBLIC_KEY_DO_PEER>
# AllowedIPs = 10.0.0.X/32
# PersistentKeepalive = 25
#
# Se o peer for um hub com IP público:
# Endpoint = <IP_PUBLICO>:51820
EOF

    log_info "Template criado: ${OUTPUT_DIR}/wg0.conf.template"
    log_warn "IMPORTANTE: Edite o template e adicione os peers antes de usar!"
}

main() {
    echo "============================================"
    echo "  MatVerse Network - Key Generator v${VERSION}"
    echo "============================================"
    echo
    
    # Parse argumentos
    for arg in "$@"; do
        case $arg in
            --node=*)
                NODE_NAME="${arg#*=}"
                ;;
            --output=*)
                OUTPUT_DIR="${arg#*=}"
                ;;
            --help)
                usage
                ;;
            *)
                log_error "Argumento desconhecido: $arg"
                usage
                ;;
        esac
    done
    
    # Validar argumentos
    if [ -z "${NODE_NAME}" ] || [ -z "${OUTPUT_DIR}" ]; then
        log_error "Argumentos obrigatórios faltando"
        usage
    fi
    
    check_wireguard
    generate_keys
    
    echo
    log_info "Concluído! Próximos passos:"
    echo "  1. Edite ${OUTPUT_DIR}/wg0.conf.template e adicione os peers"
    echo "  2. Renomeie para wg0.conf: mv ${OUTPUT_DIR}/wg0.conf.template ${OUTPUT_DIR}/wg0.conf"
    echo "  3. Copie para /etc/wireguard/: sudo cp ${OUTPUT_DIR}/wg0.conf /etc/wireguard/"
    echo "  4. Inicie WireGuard: sudo wg-quick up wg0"
}

main "$@"
