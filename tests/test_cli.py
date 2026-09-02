import json

from xref.cli import main


def test_analyze_cli_emits_machine_readable_inventory(capsys):
    assert main(["analyze", "tests/fixtures/x86_kernel"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["total"] >= 5
    assert report["by_classification"]["BACKEND"] >= 1


def test_validate_cli_reports_proof_level(capsys):
    assert main(["validate", "schemas/port-manifest.example.yaml"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report == {"highest_proved_level": "L0_ANALYZED", "port_id": "example-kernel-x86_64-riscv64", "valid": True}
