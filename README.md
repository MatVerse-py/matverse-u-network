# MatVerse Network

**Infraestrutura WireGuard e Rede Soberana**

## Visão Geral

O **MatVerse Network** implementa a camada de transporte do MatVerse Pessoal, criando uma malha WireGuard privada e criptografada que conecta todos os seus dispositivos em uma rede soberana, invisível e antifrágil.

## Arquitetura de Rede

### Topologia

```
┌─────────────────────────────────────────────────────────────┐
│                    MatVerse Network                         │
│                  Overlay: 10.0.0.0/24                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Core       │◄────►│    Twin      │                   │
│  │  10.0.0.1    │      │  10.0.0.2    │                   │
│  │  (Odyssey)   │      │ (Chromebook) │                   │
│  └──────────────┘      └──────────────┘                   │
│         ▲                      ▲                            │
│         │                      │                            │
│         ├──────────┬───────────┤                            │
│         │          │           │                            │
│  ┌──────▼────┐ ┌──▼─────┐ ┌──▼─────┐                      │
│  │  Tablet   │ │ Tablet │ │ Mobile │                      │
│  │ 10.0.0.3  │ │10.0.0.4│ │10.0.0.5│                      │
│  └───────────┘ └────────┘ └────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐      ┌─────────┐
    │ LAN/WiFi│       │  WiFi   │      │   4G    │
    │ Pública │       │ Pública │      │  Mobile │
    └─────────┘       └─────────┘      └─────────┘
```

### Propriedades da Rede

1. **Identidade Criptográfica**
   - Cada dispositivo possui um par de chaves Curve25519
   - A chave pública é a identidade do nó na rede
   - Autenticação mútua automática

2. **Zero Exposição**
   - Nenhuma porta aberta para a internet
   - Conexões peer-to-peer criptografadas
   - Invisível para scanners de rede

3. **Resiliência**
   - Reconexão automática entre nós
   - Funciona sobre qualquer rede física (LAN, WiFi, 4G, 5G)
   - Handshake a cada 2 minutos para manter túnel ativo

4. **Performance**
   - Overhead mínimo (< 5% vs. conexão direta)
   - Latência adicional: < 1ms em LAN
   - Throughput: limitado apenas pela rede física

## Estrutura do Repositório

```
matverse-u-network/
├── configs/                 # Configurações WireGuard
│   ├── core/               # Config do nó Core (Odyssey)
│   ├── twin/               # Config do nó Twin (Chromebook)
│   ├── tablet-1/           # Config Tablet 1
│   ├── tablet-2/           # Config Tablet 2
│   └── mobile/             # Config Mobile
├── scripts/                 # Scripts de automação
│   ├── generate-keys.sh    # Gerar pares de chaves
│   ├── setup-wireguard.sh  # Configurar WireGuard em um nó
│   ├── add-peer.sh         # Adicionar novo peer
│   └── health-check.sh     # Verificar conectividade
├── docs/                    # Documentação
│   ├── setup-guide.md      # Guia de configuração
│   ├── troubleshooting.md  # Resolução de problemas
│   └── security.md         # Modelo de segurança
├── tests/                   # Testes
│   ├── connectivity/       # Testes de conectividade
│   └── performance/        # Benchmarks de performance
└── README.md               # Este arquivo
```

## Início Rápido

### Pré-requisitos

- **Dispositivos**: 
  - Core: Samsung Odyssey (Windows/Linux)
  - Twin: Chromebook HP x360 (Crostini)
  - Tablets/Mobile: Android/iOS
- **WireGuard**: Instalado em todos os dispositivos
  - Linux: `sudo apt install wireguard`
  - Windows: [wireguard.com/install](https://www.wireguard.com/install/)
  - Android/iOS: App oficial da loja

### Instalação

#### 1. Gerar Chaves para Todos os Nós

```bash
# No Core (Odyssey)
cd matverse-u-network
./scripts/generate-keys.sh --node=core --output=configs/core/

# Repetir para cada nó
./scripts/generate-keys.sh --node=twin --output=configs/twin/
./scripts/generate-keys.sh --node=tablet-1 --output=configs/tablet-1/
./scripts/generate-keys.sh --node=tablet-2 --output=configs/tablet-2/
./scripts/generate-keys.sh --node=mobile --output=configs/mobile/
```

#### 2. Configurar WireGuard no Core

```bash
# Copiar configuração
sudo cp configs/core/wg0.conf /etc/wireguard/

# Iniciar interface
sudo wg-quick up wg0

# Habilitar na inicialização
sudo systemctl enable wg-quick@wg0
```

#### 3. Configurar WireGuard nos Outros Nós

```bash
# No Twin (Chromebook)
sudo cp configs/twin/wg0.conf /etc/wireguard/
sudo wg-quick up wg0

# Nos tablets/mobile: importar o arquivo .conf no app WireGuard
```

#### 4. Verificar Conectividade

```bash
# Do Core, pingar todos os nós
ping -c 3 10.0.0.2  # Twin
ping -c 3 10.0.0.3  # Tablet 1
ping -c 3 10.0.0.4  # Tablet 2
ping -c 3 10.0.0.5  # Mobile

# Verificar status do WireGuard
sudo wg show
```

## Configuração Detalhada

### Exemplo de Configuração do Core (wg0.conf)

```ini
[Interface]
# Identidade do Core
PrivateKey = <PRIVATE_KEY_CORE>
Address = 10.0.0.1/24
ListenPort = 51820

# Regras de firewall (opcional)
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peer: Twin (Chromebook)
[Peer]
PublicKey = <PUBLIC_KEY_TWIN>
AllowedIPs = 10.0.0.2/32
PersistentKeepalive = 25

# Peer: Tablet 1
[Peer]
PublicKey = <PUBLIC_KEY_TABLET1>
AllowedIPs = 10.0.0.3/32
PersistentKeepalive = 25

# Peer: Tablet 2
[Peer]
PublicKey = <PUBLIC_KEY_TABLET2>
AllowedIPs = 10.0.0.4/32
PersistentKeepalive = 25

# Peer: Mobile
[Peer]
PublicKey = <PUBLIC_KEY_MOBILE>
AllowedIPs = 10.0.0.5/32
PersistentKeepalive = 25
```

### Exemplo de Configuração de um Peer (Twin)

```ini
[Interface]
PrivateKey = <PRIVATE_KEY_TWIN>
Address = 10.0.0.2/24

# Peer: Core (hub central)
[Peer]
PublicKey = <PUBLIC_KEY_CORE>
Endpoint = <IP_PUBLICO_CORE>:51820  # Se Core tiver IP público
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
```

## Operações

### Adicionar Novo Peer

```bash
# Gerar chaves para o novo nó
./scripts/generate-keys.sh --node=new-device --output=configs/new-device/

# Adicionar peer em todos os nós existentes
./scripts/add-peer.sh --name=new-device --pubkey=<PUBLIC_KEY> --ip=10.0.0.6
```

### Revogar Peer

```bash
# Remover peer de todos os nós
sudo wg set wg0 peer <PUBLIC_KEY> remove

# Atualizar configuração permanente
sudo nano /etc/wireguard/wg0.conf  # Remover seção [Peer]
```

### Monitoramento

```bash
# Ver status e tráfego
sudo wg show wg0

# Ver logs do WireGuard
sudo journalctl -u wg-quick@wg0 -f

# Testar latência entre nós
./scripts/health-check.sh --full
```

## Segurança

### Modelo de Ameaças

- **Ameaça 1**: Interceptação de tráfego na rede pública
  - **Mitigação**: Criptografia ChaCha20-Poly1305 em todo o tráfego

- **Ameaça 2**: Personificação de nó (spoofing)
  - **Mitigação**: Autenticação mútua via chaves públicas

- **Ameaça 3**: Comprometimento de chave privada
  - **Mitigação**: Rotação de chaves, revogação imediata

### Boas Práticas

1. **Proteção de Chaves Privadas**
   - Nunca commitar chaves privadas no Git
   - Armazenar em `/etc/wireguard/` com permissões `600`
   - Fazer backup cifrado em local seguro

2. **Firewall**
   - Bloquear porta 51820 de redes públicas (se não for hub)
   - Permitir apenas tráfego WireGuard necessário

3. **Auditoria**
   - Revisar peers ativos regularmente
   - Monitorar tráfego anômalo
   - Rotacionar chaves a cada 6 meses

## Troubleshooting

### Nó não conecta

```bash
# Verificar se WireGuard está ativo
sudo wg show

# Verificar logs
sudo journalctl -u wg-quick@wg0 --no-pager -n 50

# Testar conectividade IP
ping 10.0.0.1  # Do peer para o Core

# Verificar firewall
sudo iptables -L -n -v
```

### Latência alta

```bash
# Medir latência real
ping -c 10 10.0.0.1

# Verificar MTU
ip link show wg0

# Ajustar MTU se necessário
sudo ip link set mtu 1420 dev wg0
```

### Handshake falhando

```bash
# Verificar última tentativa de handshake
sudo wg show wg0 latest-handshakes

# Forçar novo handshake
sudo wg set wg0 peer <PUBLIC_KEY> persistent-keepalive 10
```

## Performance

### Benchmarks Esperados

| Métrica | LAN | WiFi | 4G/5G |
|---------|-----|------|-------|
| Latência adicional | < 1ms | 2-5ms | 10-20ms |
| Overhead CPU | < 2% | < 5% | < 10% |
| Throughput | ~900 Mbps | ~200 Mbps | ~50 Mbps |

### Otimizações

```bash
# Aumentar buffer UDP
sudo sysctl -w net.core.rmem_max=2500000
sudo sysctl -w net.core.wmem_max=2500000

# Habilitar offload (se suportado)
sudo ethtool -K eth0 gso on gro on tso on
```

## Referências

- [WireGuard Official](https://www.wireguard.com/)
- [WireGuard Protocol](https://www.wireguard.com/protocol/)
- [MatVerse Core](../matverse-u-core) - Sistema Core + Twin
- [MatVerse Gate](../matverse-u-gate) - Autenticação SIWE
- [MatVerse Docs](../matverse-u-docs) - Documentação consolidada

---

**MatVerse Network** - A rede é a identidade. A criptografia é o transporte.
