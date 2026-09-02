from pathlib import Path

from xref.analyzer import analyze_tree, inventory
from xref.models import Classification, DebtDimension
from xref.planner import plan


FIXTURE = Path(__file__).parent / "fixtures" / "x86_kernel"


def test_finds_and_classifies_deliberate_architecture_debt():
    findings = analyze_tree(FIXTURE)
    assert any(f.rule_id == "control-register" and f.family == "address-space" for f in findings)
    assert any(f.rule_id == "port-io" and f.classification == Classification.DEVICE for f in findings)
    assert any(f.rule_id == "ordering-annotation" and f.dimension == DebtDimension.ACCIDENTAL for f in findings)


def test_backend_mechanisms_are_contained_but_still_inventoried():
    backend = [f for f in analyze_tree(FIXTURE) if f.file.startswith("arch/x86_64")]
    assert backend
    assert all(f.classification == Classification.BACKEND for f in backend)


def test_reports_and_plan_are_deterministic():
    first = analyze_tree(FIXTURE)
    assert inventory(first) == inventory(analyze_tree(FIXTURE))
    assert plan(first) == plan(analyze_tree(FIXTURE))
    assert plan(first)["warning"].endswith("not proof of portability.")
