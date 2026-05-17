# MatVerse Network Runtime v0.1

Rede mínima segura para MatVerse / ChatPriv / IA-Net.

Princípio constitucional:

```text
Internet
  ↓
Caddy :80/:443
  ↓
Ω-Gate API
  ↓
Relay efêmero RAM-only
  ↓
Ledger local append-only
```

Regra de exposição:

```text
público permitido = {80, 443}
todo o resto = rede Docker privada
```

## Subir localmente

```bash
cp .env.example .env
python3 tools/network_contract.py --compose docker-compose.yml
docker compose up --build
```

## Teste rápido

```bash
curl http://localhost/health
curl -X POST http://localhost/v1/decision \
  -H "content-type: application/json" \
  -H "x-matverse-key: change-me-before-use" \
  -d '{"event":"healthcheck","psi":0.91,"theta":1.0,"cvar":0.01,"pole":1.0,"ledger_valid":true,"replay_valid":true,"critical":false}'
```

## Não fazer

- Não publicar Redis, Postgres, Qdrant, Prometheus, Grafana ou IPFS API.
- Não abrir portas 5432, 6379, 6333, 9090, 8000, 8080.
- Não colocar chave privada, mnemonic, seed phrase ou token real em `.env`.
- Não publicar payload sensível. Publique apenas hashes, receipts e Merkle roots.
