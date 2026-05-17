# Segurança

## Bloqueios duros

- Porta pública fora de 80/443.
- Porta sensível publicada: 5432, 6379, 6333, 9090, 8501, 8502, 5000, 8000, 8080, 8787.
- `MATVERSE_API_KEY` ausente ou default em uso privilegiado.
- Evento crítico sem ledger/replay válido.
- `CVaR > 0.05`, `Ψ < 0.85`, `Ω < 0.85`.

## Publicação segura

Publicar:

- Merkle root
- receipt hash
- state hash
- evidence pack hash

Não publicar:

- private key
- seed phrase
- mnemonic
- token
- payload sensível bruto
