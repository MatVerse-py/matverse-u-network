from __future__ import annotations

import os
import time
from typing import Any

from fastapi import FastAPI, HTTPException

ROOM_TTL = int(os.getenv("RELAY_ROOM_TTL_SECONDS", "900"))
MAX_MESSAGE_BYTES = int(os.getenv("RELAY_MAX_MESSAGE_BYTES", "65536"))

app = FastAPI(title="ChatPriv Ephemeral Relay", docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "chatpriv-relay",
        "mode": "ram-only-placeholder",
        "room_ttl_seconds": ROOM_TTL,
        "max_message_bytes": MAX_MESSAGE_BYTES,
        "ts": time.time(),
    }


@app.get("/relay/stats")
def stats() -> dict[str, Any]:
    raise HTTPException(status_code=404, detail="stats are not public")


@app.get("/relay/policy")
def policy() -> dict[str, Any]:
    return {
        "persistence": "none",
        "payload_logging": False,
        "public_stats": False,
        "sensitive_payloads": "forbidden",
        "upgrade_path": "v0.2 websocket relay behind omega-gate",
    }
