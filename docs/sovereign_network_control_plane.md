# MatVerse Network Control Plane

Status: v0.2 draft

This document defines the local control plane for MatVerse Network.

## Scope

- register nodes by public identifier
- verify access requests by role, namespace and action
- record access decisions in a local append-only JSONL ledger
- support revocation through a CRL file
- emit periodic health records

## Access flow

```text
node request -> identity proof hash -> ACL -> CRL -> decision -> receipt -> ledger
```

## Ledger separation

Core ledger stores scientific evidence.
Network ledger stores access, health and operational receipts.

## v0.2 files

- seed/identity/nodes.json
- seed/identity/agents.json
- seed/policies/acl.json
- seed/policies/crl.json
- trunk/omega_gate_net/omega_gate_net.py
- trunk/ledger/access.ledger.jsonl
- branches/health/healthcheck.py

## Safety rules

- no private keys in Git
- no secrets in examples
- all identifiers are public or placeholder values
- denied requests are recorded as receipts
