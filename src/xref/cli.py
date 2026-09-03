from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze_tree, inventory
from .contracts import registry
from .manifest import ManifestError, load_manifest
from .planner import plan


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xref", description="Inspect architecture debt without claiming portability")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("analyze", "inventory", "plan"):
        command = sub.add_parser(name)
        command.add_argument("tree", type=Path)
    validate = sub.add_parser("validate")
    validate.add_argument("manifest", type=Path)
    sub.add_parser("contracts")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            data = load_manifest(args.manifest)
            _emit({"valid": True, "port_id": data["port"]["id"], "highest_proved_level": data["port"]["highest_proved_level"]})
        elif args.command == "contracts":
            _emit({"contracts": registry()})
        else:
            findings = analyze_tree(args.tree)
            if args.command in {"analyze", "inventory"}:
                _emit(inventory(findings))
            else:
                _emit(plan(findings))
    except (ManifestError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
