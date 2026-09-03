from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from xref.contracts import registry
from xref.manifest import ManifestError, load_manifest, validate_manifest


EXAMPLE = Path(__file__).parents[1] / "schemas" / "port-manifest.example.yaml"


def test_example_manifest_is_valid():
    manifest = load_manifest(EXAMPLE)
    assert manifest["port"]["source_arch"] == "x86_64"


def test_manifest_rejects_unproved_claim_overlap():
    manifest = yaml.safe_load(EXAMPLE.read_text())
    manifest = deepcopy(manifest)
    manifest["claims"]["allowed"].append("RV64 port works")
    with pytest.raises(ManifestError, match="both allowed and forbidden"):
        validate_manifest(manifest)


def test_manifest_rejects_duplicate_contract_identity():
    manifest = yaml.safe_load(EXAMPLE.read_text())
    manifest["contracts"].append(deepcopy(manifest["contracts"][0]))
    with pytest.raises(ManifestError, match="duplicate contract id"):
        validate_manifest(manifest)


def test_contract_registry_is_complete_and_stable():
    records = registry()
    assert [record["id"] for record in records] == sorted(record["id"] for record in records)
    assert {record["name"] for record in records} >= {"address-space-activate", "memory-order-enforce"}
