# Foundation tooling

The first X-REF tool is deliberately a conservative inventory and state-model
foundation. It does not translate code and it does not infer that a compiling
target is portable.

Install it in a development environment and inspect a kernel-like tree:

```sh
python -m pip install -e '.[test]'
xref validate schemas/port-manifest.example.yaml
xref analyze /path/to/kernel > inventory.json
xref plan /path/to/kernel > plan.json
xref contracts > contracts.json
```

`analyze` and `inventory` produce the same deterministic JSON document. Each
finding records its exact location, matched evidence, semantic family,
classification, debt dimension, confidence, rationale, and a next inspection.
The lexical rules currently recognize high-value x86 dependencies; because a
lexical match cannot establish intent, semantic classifications use medium
confidence and ambiguous synchronization is `UNKNOWN`.

Code already under `arch/x86_64` or `backend/x86_64` remains visible but is
classified as contained `BACKEND` machinery. This prevents a misleading clean
inventory while ensuring contained machine mechanisms do not receive the same
urgency as leaks in common code.

`validate` turns the example manifest into enforced durable state. It checks
the major state sections, architecture direction, proof levels, contract
identity and maturity, and contradictory claim gates. It is structural
validation, not evidence that recorded commands ran.

The built-in contract registry seeds reusable semantic records for address
space activation, translation invalidation, interrupt state, and explicit
memory ordering. Architecture mechanisms appear only in source/target mapping
notes.

## What became possible

An agent can now produce a repeatable architecture-debt inventory, distinguish
contained x86 backend code from common-code leakage, persist port state, inspect
the initial semantic contract vocabulary, and generate bounded review batches.
Tests exercise deliberate CR3, inline assembly, port-I/O, and TSO assumptions.

No command claims that the fixture or an analyzed kernel is portable. The plan
explicitly states that static analysis is only an inspection queue.

## Next causal step

Run this inventory on a small booting x86 kernel and select its first boot
pressure. Trace callers around the first critical finding, define or refine one
contract from observed behavior, adapt the x86 path through it, and record a
source regression artifact. Only after that source-preservation gate should an
RV64 implementation and conformance fixture be added. Compiler-derived symbol
and call-graph provenance is the next analyzer layer once lexical findings have
been tested against that real codebase.
