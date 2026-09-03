from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Classification(str, Enum):
    CONTRACT = "CONTRACT"
    BACKEND = "BACKEND"
    ACCIDENTAL = "ACCIDENTAL"
    ABI = "ABI"
    DEVICE = "DEVICE"
    UNKNOWN = "UNKNOWN"


class DebtDimension(str, Enum):
    DIRECT = "DIRECT"
    STRUCTURAL = "STRUCTURAL"
    BEHAVIORAL = "BEHAVIORAL"
    ORDERING = "ORDERING"
    PLATFORM = "PLATFORM"
    ABI = "ABI"
    ACCIDENTAL = "ACCIDENTAL"


@dataclass(frozen=True, order=True)
class Finding:
    file: str
    line: int
    column: int
    rule_id: str
    evidence: str
    family: str
    classification: Classification
    dimension: DebtDimension
    confidence: str
    reason: str
    next_inspection: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["classification"] = self.classification.value
        value["dimension"] = self.dimension.value
        return value
