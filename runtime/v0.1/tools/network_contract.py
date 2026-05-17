#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PUBLIC_ALLOWLIST = {"80", "443"}
SENSITIVE_PORTS = {"5432", "6379", "6333", "9090", "8501", "8502", "5000", "8000", "8080", "8787"}
PORT_RE = re.compile(r'["\']?(\d{2,5})\s*:\s*(\d{2,5})["\']?')
TOP_LEVEL_SERVICES_RE = re.compile(r"^services\s*:", re.MULTILINE)


def find_ports(text: str) -> list[tuple[str, str]]:
    return PORT_RE.findall(text)


def validate_compose(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, str]] = []

    if len(TOP_LEVEL_SERVICES_RE.findall(text)) != 1:
        findings.append({
            "severity": "high",
            "flag": "neycsec01.yaml_structural_risk",
            "evidence": "compose must have exactly one top-level services key",
            "solution": "Run docker compose config and fix duplicated top-level sections.",
        })

    for host, container in find_ports(text):
        if host not in PUBLIC_ALLOWLIST:
            findings.append({
                "severity": "critical" if host in SENSITIVE_PORTS else "high",
                "flag": "neycsec01.public_sensitive_port",
                "evidence": f"host_port={host}, container_port={container}",
                "solution": f"Remove host port {host}; keep service behind internal Docker network.",
            })

    internal_networks = {"app", "data", "ledger", "obs"}
    for network in internal_networks:
        pattern = rf"{network}:\n(?:\s+name: .+\n)?\s+internal:\s+true"
        if not re.search(pattern, text):
            findings.append({
                "severity": "medium",
                "flag": "neycsec01.network_not_internal",
                "evidence": f"network={network}",
                "solution": f"Set networks.{network}.internal=true.",
            })

    decision = "allow" if not any(f["severity"] in {"critical", "high"} for f in findings) else "deny"
    return {
        "summary": {
            "omega_gate": decision,
            "findings": len(findings),
            "public_allowlist": sorted(PUBLIC_ALLOWLIST),
        },
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose", type=Path, default=Path("docker-compose.yml"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate_compose(args.compose)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Ω-Gate: {report['summary']['omega_gate']}")
        for f in report["findings"]:
            print(f"- {f['severity']} {f['flag']}: {f['evidence']}")

    return 0 if report["summary"]["omega_gate"] == "allow" else 2


if __name__ == "__main__":
    raise SystemExit(main())
