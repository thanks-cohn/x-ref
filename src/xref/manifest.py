from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ManifestError(ValueError):
    pass


MATURITY = {"DISCOVERED", "DEFINED", "SOURCE_ADAPTED", "SOURCE_PROVED", "TARGET_IMPLEMENTED", "TARGET_PROVED", "PORTABLE"}
LEVELS = {f"L{i}_{name}" for i, name in enumerate(("ANALYZED", "ISOLATED", "SOURCE_PROVED", "TARGET_BOOT", "TARGET_USER", "TARGET_WORKLOAD", "DIFFERENTIAL", "PORTABLE"))}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ManifestError(str(exc)) from exc
    validate_manifest(data)
    return data


def validate_manifest(data: object) -> None:
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a mapping")
    required = {"xref_version", "project", "port", "pressure", "inventory", "contracts", "workstreams", "evidence", "invariants", "non_equivalence_ledger", "agent_batches", "claims"}
    missing = sorted(required - data.keys())
    if missing:
        raise ManifestError("missing required fields: " + ", ".join(missing))
    _keys(data["project"], "project", {"name", "source_repository", "source_revision"})
    _keys(data["port"], "port", {"id", "source_arch", "target_arch", "target_platform", "status", "highest_proved_level"})
    _keys(data["pressure"], "pressure", {"current", "next_success_condition", "next_causal_blocker"})
    if data["port"]["source_arch"] == data["port"]["target_arch"]:
        raise ManifestError("source_arch and target_arch must differ")
    if data["port"]["highest_proved_level"] not in LEVELS:
        raise ManifestError("port.highest_proved_level is not a recognized proof level")
    if not isinstance(data["contracts"], list):
        raise ManifestError("contracts must be a list")
    seen: set[str] = set()
    for i, contract in enumerate(data["contracts"]):
        _keys(contract, f"contracts[{i}]", {"id", "name", "family", "maturity", "required", "source", "target", "known_non_equivalences"})
        if contract["id"] in seen:
            raise ManifestError(f"duplicate contract id: {contract['id']}")
        seen.add(contract["id"])
        if contract["maturity"] not in MATURITY:
            raise ManifestError(f"invalid maturity for {contract['id']}")
    claims = data["claims"]
    _keys(claims, "claims", {"allowed", "forbidden_until_proved"})
    overlap = set(claims["allowed"]) & set(claims["forbidden_until_proved"])
    if overlap:
        raise ManifestError("claims cannot be both allowed and forbidden: " + ", ".join(sorted(overlap)))


def _keys(value: object, where: str, required: set[str]) -> None:
    if not isinstance(value, dict):
        raise ManifestError(f"{where} must be a mapping")
    missing = sorted(required - value.keys())
    if missing:
        raise ManifestError(f"{where} missing: " + ", ".join(missing))
