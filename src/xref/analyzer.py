from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import Classification, DebtDimension, Finding


@dataclass(frozen=True)
class Rule:
    id: str
    pattern: re.Pattern[str]
    family: str
    classification: Classification
    dimension: DebtDimension
    reason: str


def _rule(id: str, pattern: str, family: str, classification: Classification,
          dimension: DebtDimension, reason: str) -> Rule:
    return Rule(id, re.compile(pattern, re.IGNORECASE), family, classification, dimension, reason)


RULES = (
    _rule("inline-assembly", r"\b(?:__asm__|__asm|asm)\s*(?:volatile\s*)?\(", "cpu", Classification.CONTRACT, DebtDimension.DIRECT, "Inline assembly couples this source location to an instruction set."),
    _rule("control-register", r"(?<![A-Za-z0-9_])(?:cr[0234]|invlpg|invpcid)(?![A-Za-z0-9_])", "address-space", Classification.CONTRACT, DebtDimension.DIRECT, "Control-register or TLB machinery suggests translation semantics."),
    _rule("privileged-state", r"(?<![A-Za-z0-9_])(?:cli|sti|hlt|lgdt|lidt|ltr|rdmsr|wrmsr)(?![A-Za-z0-9_])", "cpu", Classification.CONTRACT, DebtDimension.DIRECT, "Privileged x86 state must be understood at a semantic boundary."),
    _rule("entry-abi", r"(?<![A-Za-z0-9_])(?:iretq?|syscall|sysret)(?![A-Za-z0-9_])", "userspace-entry", Classification.ABI, DebtDimension.ABI, "Entry/return machinery encodes privilege and ABI behavior."),
    _rule("cpu-discovery", r"(?<![A-Za-z0-9_])(?:cpuid|__rdtsc)(?![A-Za-z0-9_])", "cpu", Classification.CONTRACT, DebtDimension.DIRECT, "CPU discovery or counter access needs a portable requirement."),
    _rule("x86-intrinsic", r"\b(?:__builtin_ia32_[A-Za-z0-9_]*|_mm_[A-Za-z0-9_]*)", "cpu", Classification.BACKEND, DebtDimension.DIRECT, "An x86 compiler intrinsic is an implementation-specific mechanism."),
    _rule("interrupt-controller", r"\b(?:ioapic|apic)\b", "interrupt", Classification.DEVICE, DebtDimension.PLATFORM, "Interrupt controllers are platform facilities, not ISA translations."),
    _rule("port-io", r"\b(?:inb|inw|inl|outb|outw|outl)\s*\(", "io", Classification.DEVICE, DebtDimension.PLATFORM, "Legacy port I/O is a platform/device assumption."),
    _rule("machine-table", r"\b(?:idt|gdt|tss)\b", "exception", Classification.CONTRACT, DebtDimension.STRUCTURAL, "A common structure may mirror x86 exception or privilege formats."),
    _rule("atomic-ordering", r"\b(?:__atomic_|atomic_thread_fence|cmpxchg|xchg|LOCK_PREFIX)\b", "ordering", Classification.UNKNOWN, DebtDimension.ORDERING, "Synchronization requires review against RVWMO; syntax alone cannot prove intent."),
    _rule("ordering-annotation", r"XREF_ORDERING_REVIEW|x86\s+TSO|TSO-dependent", "ordering", Classification.ACCIDENTAL, DebtDimension.ACCIDENTAL, "The source explicitly identifies reliance on x86 ordering."),
    _rule("boot-firmware", r"\b(?:multiboot|acpi|uefi)\b", "boot", Classification.UNKNOWN, DebtDimension.PLATFORM, "Boot/firmware coupling must be separated from ISA coupling."),
)

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".s", ".S", ".asm"}


def analyze_tree(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in SOURCE_SUFFIXES):
        rel = path.relative_to(root).as_posix()
        backend = bool(re.search(r"(^|/)(arch|backend)/x86(?:_64)?(/|$)", rel, re.I))
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if path.suffix.lower() in {".s", ".asm"}:
            findings.append(Finding(rel, 1, 1, "assembly-file", path.name, "context", Classification.BACKEND if backend else Classification.UNKNOWN, DebtDimension.DIRECT, "high" if backend else "medium", "An assembly translation unit is architecture-coupled.", "Determine the kernel-visible behavior implemented by this file."))
        for number, line in enumerate(lines, 1):
            for rule in RULES:
                for match in rule.pattern.finditer(line):
                    classification = Classification.BACKEND if backend and rule.classification not in {Classification.ABI, Classification.DEVICE} else rule.classification
                    confidence = "high" if classification in {Classification.BACKEND, Classification.DEVICE} else "medium"
                    reason = rule.reason + (" The mechanism is already contained in an x86 backend." if backend else "")
                    findings.append(Finding(rel, number, match.start() + 1, rule.id, match.group(0), rule.family, classification, rule.dimension, confidence, reason, "Inspect callers and document the required behavior before rewriting."))
    return sorted(findings)


def inventory(findings: list[Finding]) -> dict[str, object]:
    by_class = {kind.value: sum(f.classification is kind for f in findings) for kind in Classification}
    by_family = {family: sum(f.family == family for f in findings) for family in sorted({f.family for f in findings})}
    return {"total": len(findings), "by_classification": by_class, "by_family": by_family,
            "findings": [f.to_dict() for f in findings]}
