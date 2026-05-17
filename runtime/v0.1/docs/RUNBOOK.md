# Runbook

## Validação

```bash
python3 tools/network_contract.py --compose docker-compose.yml --json
docker compose config
```

## Subir

```bash
cp .env.example .env
docker compose up --build
```

## Logs

```bash
docker compose logs -f edge omega-api chatpriv-relay
```

## Destruir ambiente local

```bash
docker compose down -v
rm -f data/ledger/events.jsonl
```
