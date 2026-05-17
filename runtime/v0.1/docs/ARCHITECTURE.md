# Arquitetura MatVerse Network Runtime v0.1

## Princípio

```text
público permitido = {80, 443}
todo o resto = privado por padrão
```

## Topologia

```text
Internet
  ↓
Caddy Edge :80/:443
  ↓
Ω-Gate API
  ↓
ChatPriv Relay efêmero
  ↓
Ledger append-only local
```

## Zonas

| Zona | Exposição | Conteúdo |
|---|---:|---|
| Edge | 80/443 | Caddy, headers, reverse proxy |
| App | privada | omega-api, chatpriv-relay |
| Data | privada | Redis/Postgres opcionais |
| Ledger | privada | JSONL append-only |
| Obs | privada | Prometheus opcional |

## Contrato

```text
evento → detector → flag neycsec01 → Ω-Gate → bloqueio → solução
```
