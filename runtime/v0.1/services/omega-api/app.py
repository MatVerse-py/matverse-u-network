from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

APP_VERSION = "matverse-network-v0.1"
LEDGER_PATH = Path(os.getenv("LEDGER_PATH", "/data/ledger/events.jsonl"))
API_KEY = os.getenv("MATVERSE_API_KEY", "")

MIN_PSI = float(os.getenv("MIN_PSI", "0.85"))
MAX_CVAR = float(os.getenv("MAX_CVAR", "0.05"))
MIN_OMEGA = float(os.getenv("MIN_OMEGA", "0.85"))

app = FastAPI(
    title="MatVerse Ω-Gate API",
    version=APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class DecisionRequest(BaseModel):
    event: str = Field(min_length=1, max_length=128)
    psi: float = Field(ge=0.0, le=1.0)
    theta: float = Field(ge=0.0, le=1.0)
    cvar: float = Field(ge=0.0, le=1.0)
    pole: float = Field(ge=0.0, le=1.0)
    ledger_valid: bool = False
    replay_valid: bool = False
    critical: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CoherenceRequest(BaseModel):
    temporal_coherence: float = Field(ge=0.0, le=1.0)
    semantic_coherence: float = Field(ge=0.0, le=1.0)
    recovery_rate: float = Field(ge=0.0, le=1.0)
    entropy_drift: float = Field(ge=0.0, le=1.0)
    causal_admissibility: float = Field(ge=0.0, le=1.0)


def require_key(x_matverse_key: str | None) -> None:
    if not API_KEY or API_KEY == "change-me-before-use":
        raise HTTPException(
            status_code=503,
            detail="MATVERSE_API_KEY must be configured before privileged use.",
        )
    if not x_matverse_key or not hmac.compare_digest(x_matverse_key, API_KEY):
        raise HTTPException(status_code=401, detail="invalid api key")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def merkle_root(hashes: list[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    layer = [bytes.fromhex(h) for h in hashes]
    while len(layer) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            nxt.append(hashlib.sha256(left + right).digest())
        layer = nxt
    return layer[0].hex()


def append_ledger(record: dict[str, Any]) -> dict[str, Any]:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = dict(record)
    record["state_hash"] = sha256_hex(record)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(canonical_json(record) + "\n")
    return record


def read_ledger_hashes(limit: int = 2048) -> list[str]:
    if not LEDGER_PATH.exists():
        return []
    lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
    out: list[str] = []
    for line in lines:
        try:
            obj = json.loads(line)
            state_hash = obj.get("state_hash")
            if isinstance(state_hash, str) and len(state_hash) == 64:
                out.append(state_hash)
        except json.JSONDecodeError:
            continue
    return out


def compute_omega(req: DecisionRequest) -> float:
    return max(
        0.0,
        min(
            1.0,
            0.4 * req.psi
            + 0.3 * req.theta
            + 0.2 * (1.0 - req.cvar)
            + 0.1 * req.pole,
        ),
    )


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "omega-api",
        "version": APP_VERSION,
        "public_surface": ["GET /health"],
    }


@app.post("/v1/decision")
def decision(req: DecisionRequest, x_matverse_key: str | None = Header(default=None)) -> dict[str, Any]:
    require_key(x_matverse_key)

    omega = compute_omega(req)
    flags: list[str] = []

    if req.psi < MIN_PSI:
        flags.append("neycsec01.psi_low")
    if req.cvar > MAX_CVAR:
        flags.append("neycsec01.cvar_high")
    if omega < MIN_OMEGA:
        flags.append("neycsec01.omega_low")
    if not req.ledger_valid:
        flags.append("neycsec01.invalid_ledger")
    if not req.replay_valid:
        flags.append("neycsec01.invalid_replay")
    if req.critical:
        flags.append("neycsec01.critical_event")

    verdict = "ALLOW" if not flags else "BLOCK"

    receipt = {
        "ts": time.time(),
        "event": req.event,
        "input_hash": sha256_hex(req.model_dump()),
        "metrics": {
            "psi": req.psi,
            "theta": req.theta,
            "cvar": req.cvar,
            "pole": req.pole,
            "omega": omega,
        },
        "policy": {
            "min_psi": MIN_PSI,
            "max_cvar": MAX_CVAR,
            "min_omega": MIN_OMEGA,
            "fail_closed": True,
        },
        "verdict": verdict,
        "flags": flags,
        "metadata": req.metadata,
    }

    record = append_ledger(receipt)
    root = merkle_root(read_ledger_hashes())

    return {
        "verdict": verdict,
        "flags": flags,
        "omega": omega,
        "receipt": record,
        "ledger_merkle_root": root,
    }


@app.post("/v1/coherence")
def coherence(req: CoherenceRequest, x_matverse_key: str | None = Header(default=None)) -> dict[str, Any]:
    require_key(x_matverse_key)

    psi = max(
        0.0,
        min(
            1.0,
            0.25 * req.temporal_coherence
            + 0.25 * req.semantic_coherence
            + 0.20 * req.recovery_rate
            + 0.15 * (1.0 - req.entropy_drift)
            + 0.15 * req.causal_admissibility,
        ),
    )

    flags: list[str] = []
    if psi < MIN_PSI:
        flags.append("neycsec01.coherence_low")
    if req.entropy_drift > 0.20:
        flags.append("neycsec01.entropy_drift_high")

    record = append_ledger({
        "ts": time.time(),
        "event": "coherence_index",
        "metrics": req.model_dump(),
        "psi": psi,
        "verdict": "ALLOW" if not flags else "REVIEW",
        "flags": flags,
    })

    return {
        "psi": psi,
        "verdict": record["verdict"],
        "flags": flags,
        "receipt": record,
        "ledger_merkle_root": merkle_root(read_ledger_hashes()),
    }


@app.get("/v1/ledger/root")
def ledger_root(x_matverse_key: str | None = Header(default=None)) -> dict[str, Any]:
    require_key(x_matverse_key)
    hashes = read_ledger_hashes()
    return {
        "events": len(hashes),
        "merkle_root": merkle_root(hashes),
        "ledger_path": str(LEDGER_PATH),
    }
