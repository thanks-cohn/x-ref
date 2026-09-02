from __future__ import annotations

from .models import Classification, Finding


def plan(findings: list[Finding]) -> dict[str, object]:
    unresolved = [f for f in findings if f.classification != Classification.BACKEND]
    families = sorted({f.family for f in unresolved})
    batches = []
    for index, family in enumerate(families, 1):
        sites = sum(f.family == family for f in unresolved)
        batches.append({"id": f"batch-{index:03d}", "family": family, "sites": sites,
                        "objective": f"inspect and isolate {family} semantics",
                        "success_gate": "source behavior is preserved by recorded evidence before target implementation"})
    return {"summary": {"findings": len(findings), "already_contained": len(findings) - len(unresolved), "semantic_review_sites": len(unresolved)},
            "warning": "This static plan is an inspection queue, not proof of portability.", "suggested_batches": batches}
