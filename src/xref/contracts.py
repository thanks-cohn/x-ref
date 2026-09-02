from __future__ import annotations

import json
from importlib.resources import files


def registry() -> list[dict[str, object]]:
    records = json.loads(files("xref.data").joinpath("contracts.json").read_text(encoding="utf-8"))
    required = {"id", "name", "family", "intent", "inputs", "outputs", "preconditions", "postconditions", "ordering", "privilege", "failure_semantics", "source_mapping", "target_mapping", "known_non_equivalences", "maturity", "source_evidence", "target_evidence"}
    ids = set()
    for record in records:
        missing = required - record.keys()
        if missing:
            raise ValueError(f"contract {record.get('id', '?')} missing {sorted(missing)}")
        if record["id"] in ids:
            raise ValueError(f"duplicate contract id {record['id']}")
        ids.add(record["id"])
    return sorted(records, key=lambda item: str(item["id"]))
