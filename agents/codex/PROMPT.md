# X-REF Codex Foundation Prompt

You are working inside **X-REF**, an agent-assisted kernel architecture-porting project.

Your task is not to make a toy demo, not to produce a one-off RISC-V fork, and not to maximize generated code.

Your task is to **build the foundation that can make real kernel ports dramatically faster than conventional architecture ports**.

The central hypothesis of this repository is:

> A large kernel port should not require engineers to rediscover every machine assumption by hand. If architecture dependencies can be discovered, classified, converted into semantic contracts, preserved on the source machine, and reimplemented behind the same contracts on the target machine, then agents can compress a large portion of the traditional porting cycle.

X-REF exists to test whether an architecture port that might traditionally consume many years can be reduced by a substantial fraction through disciplined machine contracts, reusable migration knowledge, automated architecture-debt discovery, differential evidence, and parallel agent work.

A useful working ambition is **approximately 50% reduction in total porting time** on serious kernels.

Treat that number as an engineering hypothesis and optimization target, **not as a claim already proved by this repository**.

The long-term dream is that something which might otherwise consume a decade of architecture work could plausibly become a project measured in a few years, and that smaller or cleaner kernels could move dramatically faster still.

The product is therefore not merely an RV64 backend.

The product is **porting acceleration itself**.

---

# Mission

Build X-REF into a reusable system where this increasingly becomes possible:

```text
existing x86-64 kernel
        |
        v
X-REF discovers architecture debt
        |
        v
agents classify machine assumptions
        |
        v
semantic machine contracts are introduced
        |
        v
x86-64 behavior is preserved and proved
        |
        v
agents implement equivalent RV64 semantics
        |
        v
source/target evidence is compared
        |
        v
working RISC-V kernel
```

To the user, the experience should eventually feel almost magical:

> Give X-REF your x86 kernel and watch agents drive it toward a working RISC-V port in record time.

Underneath, there must be no magic.

There must be:

```text
assumption
 -> classification
 -> semantic contract
 -> source adaptation
 -> source proof
 -> target implementation
 -> target proof
 -> reusable port knowledge
```

That chain is the architecture.

---

# Read before changing anything

Before implementation, inspect and internalize:

```text
README.md
agents/PORTING_PROTOCOL.md
contracts/MACHINE_CONTRACT.md
docs/ARCHITECTURE.md
mappings/x86_64-riscv64.md
include/xref/machine.h
schemas/port-manifest.example.yaml
```

These files define the current philosophy.

Do not casually replace their central ideas with a different portability model.

If a conflict exists between convenience and the core design, preserve the core design unless the implementation proves that a change is necessary.

---

# Core tenet

## PORT SEMANTICS, NOT INSTRUCTIONS

This is the non-negotiable design law of X-REF.

Bad transformation:

```text
x86 CR3 operation
    -> agent searches for a RISC-V equivalent instruction
    -> SATP operation appears in approximately the same source location
```

Correct transformation:

```text
x86 CR3 operation
    -> determine why the kernel performs it
    -> define address-space activation semantics
    -> route the working x86 implementation through that contract
    -> prove x86 behavior unchanged
    -> implement the same contract naturally with SATP/SFENCE.VMA
```

The target architecture must not be forced to cosplay as the source architecture.

The common kernel should express **what it requires**.

The architecture backends should express **how their machines satisfy it**.

---

# What you are building now

This is a foundation task.

Do not attempt to port Linux, BSD, SerenityOS, or another enormous kernel immediately.

Build the machinery that makes future ports faster.

Your implementation should establish a credible first X-REF toolchain with the following capabilities.

## 1. Repository/project model

Create a coherent implementation layout for X-REF itself.

Prefer a small number of obvious top-level concepts such as:

```text
src/
    analyzer/
    contracts/
    planner/
    evidence/
    manifest/
    cli/

tests/
fixtures/
tools/
```

Do not create directories merely to make the repository look sophisticated.

Every component should support the port-acceleration mission.

## 2. Port manifest implementation

Turn the example manifest in:

```text
schemas/port-manifest.example.yaml
```

into an actually validated project model.

The implementation should be able to represent at minimum:

```text
source repository
source revision
source architecture
target architecture
target platform
current pressure
next success condition
next causal blocker
architecture dependency inventory
contracts
contract maturity
workstreams
evidence
invariants
non-equivalence ledger
agent batches
allowed claims
forbidden claims
```

The manifest should become the durable state of an X-REF migration rather than transient agent memory.

Prefer deterministic serialization and validation.

## 3. Architecture-debt analyzer foundation

Implement the first real analyzer for C/C++-style kernel trees.

The first version may be static/lexical, but design it so compiler and runtime evidence can be added later.

It should discover and classify likely architecture dependencies such as:

```text
inline assembly
.S / .asm files
privileged instructions
x86 register names
control registers
MSRs
CPUID
IDT/GDT/TSS assumptions
APIC/IOAPIC references
port I/O
TLB operations
page-table encodings
architecture intrinsics
compiler builtins
context-switch assembly
syscall entry assembly
atomics
fences/barriers
CPU-local storage
boot protocol dependencies
firmware dependencies
machine constants
```

For x86-64 specifically, recognize common signals including but not limited to:

```text
cr0 cr2 cr3 cr4
rdmsr wrmsr
invlpg invpcid
cli sti hlt
lgdt lidt ltr
iret iretq
syscall sysret
cpuid
xsave xrstor
fxsave fxrstor
lock
cmpxchg
xchg
inb inw inl
outb outw outl
apic ioapic
idt gdt tss
__rdtsc
__builtin_ia32_*
_mm_*
```

Do not simply return grep output.

Produce structured findings with fields such as:

```text
file
line
symbol/context
matched evidence
suspected semantic family
classification confidence
reason
suggested next inspection
```

## 4. Classification engine

Support the X-REF architecture-debt classifications:

```text
CONTRACT
BACKEND
ACCIDENTAL
ABI
DEVICE
UNKNOWN
```

Also support debt dimensions from the architecture document:

```text
DIRECT
STRUCTURAL
BEHAVIORAL
ORDERING
PLATFORM
ABI
ACCIDENTAL
```

It is acceptable for the early classifier to be heuristic.

It is not acceptable for it to pretend certainty.

Confidence and provenance should be visible.

Prefer `UNKNOWN` over fabrication.

## 5. Machine contract registry

Create a structured registry for semantic machine contracts.

Seed it with a small number of high-value contracts derived from the existing framework, such as:

```text
address-space activation
translation invalidation
interrupt enable/disable
inter-processor notification
kernel context switch
userspace entry
timer read/program
CPU identity
memory fence / ordering requirement
MMIO primitive
```

A contract record should be able to describe:

```text
id
name
family
intent
inputs
outputs
preconditions
postconditions
ordering
privilege
failure semantics
source mapping
target mapping
known non-equivalences
maturity
source evidence
target evidence
```

The registry must distinguish semantic contracts from architecture-specific implementation notes.

## 6. Port planner

Build the first planner that transforms analyzer findings into bounded porting work.

Given a manifest and architecture inventory, it should be able to produce something like:

```text
Port readiness: 31%

Critical semantic blockers:
1. address-space activation
2. trap entry
3. context restore
4. timer source
5. x86 memory-order assumption in scheduler queue

Suggested batches:
A. isolate address-space activation behind XREF-MM-001
B. preserve x86 behavior with source regression fixture
C. add RV64 implementation and QEMU conformance fixture
D. normalize trap entry semantics
...
```

The planner should favor **causal progress** over broad speculative rewriting.

When runtime pressure is available, the next batch should follow the first real blocker.

## 7. Evidence model

Implement evidence records as first-class objects.

X-REF must never collapse:

```text
compiles
```

into:

```text
works
```

Distinguish at minimum:

```text
STATIC
BUILD
UNIT
CONFORMANCE
BOOT
WORKLOAD
DIFFERENTIAL
MUTATION
INVARIANT
```

Evidence records should contain:

```text
command or procedure
source revision
target revision
architecture
result
artifact/reference
observed semantic facts
limitations
```

## 8. Claim gates

Implement a mechanism that prevents the system from claiming higher maturity than the evidence supports.

For example:

```text
L0 ANALYZED
L1 ISOLATED
L2 SOURCE-PROVED
L3 TARGET-BOOT
L4 TARGET-USER
L5 TARGET-WORKLOAD
L6 DIFFERENTIAL
L7 PORTABLE
```

A project at L3 must not be described by tooling as behaviorally equivalent.

A backend that compiles must not be described as booting.

This discipline matters because trust is part of the acceleration strategy.

## 9. Initial CLI

Create a minimal but real CLI surface.

A useful direction is:

```text
xref init
xref analyze
xref inventory
xref contracts
xref plan
xref status
xref validate
xref evidence
```

The first commands do not need every future feature.

They do need deterministic useful output and tests.

An eventual workflow should resemble:

```text
xref init ../kernel --source x86_64 --target riscv64
xref analyze
xref plan
xref status
```

Do not implement a fake `xref port` command that implies autonomous kernel translation before the machinery exists.

## 10. Fixtures

Add small synthetic kernel-like fixtures that intentionally contain architecture debt.

For example:

```text
fixture_x86_simple/
    paging
    interrupt state
    context entry
    atomics
```

Use these to prove that the analyzer and planner recognize relevant patterns.

Include both obvious and deceptive cases:

```text
direct CR3 write
wrapper around CR3 write
x86-only constant in common structure
TSO-dependent publication pattern annotation
port-I/O device assumption
architecture-specific code correctly contained in backend
```

The analyzer should not flag clean backend-contained code with the same urgency as architecture leakage into common code.

---

# The acceleration objective

Every design decision should be evaluated against one question:

> Does this reduce the amount of novel human reasoning required to port the next real kernel?

X-REF is not trying to reduce port time by generating code faster alone.

The larger gains should come from eliminating repeated rediscovery.

Traditional architecture work repeatedly spends time on:

```text
finding hidden assumptions
understanding why they exist
identifying target equivalents
reconstructing invariants
writing one-off tests
rediscovering memory-order bugs
debugging late crashes caused by early semantic divergence
repeating lessons already learned in other ports
```

X-REF should capture those lessons as reusable machinery.

A successful port should leave behind:

```text
new analyzer signatures
new classifications
new contracts
new mappings
new conformance fixtures
new failure signatures
new evidence strategies
new planner knowledge
```

The second kernel should therefore be easier than the first.

The tenth should be easier than the second.

This compounding effect is the deeper mechanism by which a 50% reduction could become plausible.

---

# Performance metric: PORT ACCELERATION

Begin laying the groundwork for eventually measuring X-REF's actual benefit.

Do not claim acceleration without evidence.

Design metrics that could later compare:

```text
baseline estimated port effort
X-REF-assisted port effort
architecture sites discovered automatically
contracts reused from prior ports
human-design decisions required
agent-resolved tasks
mean time from first divergence to repair
regressions introduced
source behavior preserved
number of target milestones reached
```

A simple conceptual metric is:

```text
acceleration_ratio = assisted_effort / baseline_effort
```

where lower is better.

The aspirational threshold:

```text
assisted effort <= 0.5 * conventional effort
```

Again: this is a target to investigate, not a result to advertise prematurely.

Because multi-year kernel ports cannot always be experimentally replayed, the framework should support multiple evidence sources for baselines:

```text
historical port timelines
issue/commit histories
maintainer estimates
architecture-diff size
human intervention counts
controlled smaller-kernel experiments
```

Keep provenance explicit.

---

# Time-scale philosophy

Do not dismiss a 50% improvement because the percentage sounds modest.

For large systems, percentage improvements multiply against enormous baselines.

Conceptually:

```text
10-year conventional effort
        -> 5 years

6-year conventional effort
        -> 3 years

2-year conventional effort
        -> 1 year

12-month conventional effort
        -> 6 months
```

Whether X-REF can actually achieve those reductions must be proven experimentally.

But the repository should be built for that scale of ambition.

Optimize for shaving **years**, not just keystrokes.

---

# Memory ordering must be treated as a major port domain

x86-64 -> RV64 is deliberately difficult because x86 TSO can hide assumptions that fail under RVWMO.

The foundation should explicitly support an **ordering audit**.

Do not solve ordering bugs by blindly inserting fences into RV64 code until tests stop failing.

X-REF should eventually help identify patterns where:

```text
source code relies on stronger ordering than its abstractions express
```

and transform that into:

```text
explicit semantic synchronization requirement
        |
        +--> valid x86 implementation
        +--> valid RV64 implementation
```

Ordering discoveries should be reusable knowledge.

---

# ISA vs platform distinction

Do not conflate x86 architecture with PC platform history.

Examples that require classification rather than automatic translation:

```text
APIC
IOAPIC
HPET
ACPI
UEFI
legacy port I/O
PCI assumptions
Multiboot
SBI
PLIC
AIA
device tree
```

Some are ISA-adjacent, some are platform, firmware, or device concerns.

X-REF must make those boundaries clearer rather than burying them.

---

# Do not overfit to x86 -> RV64

That is the first proving pair, not the eternal architecture of the framework.

Whenever you design a common abstraction, ask:

> Would this still make sense for ARM64?

And, where useful:

> Could this eventually make sense for a WASM-hosted machine personality or hypervisor backend?

Do not implement ARM64/WASM/hypervisor support now unless it naturally falls out of the work.

Use them as abstraction tests.

---

# Language choice

Use a language/tooling stack that maximizes maintainability, analyzability, deterministic testing, and ease of agent modification.

The current public machine-interface skeleton is C because the framework targets kernels commonly written in C/C++ and needs an extremely portable semantic boundary.

The X-REF analysis tooling itself does not have to be C.

Choose implementation languages pragmatically.

For the first tooling foundation, Python is acceptable and may be preferable for speed of iteration, structured parsing, testing, and agent accessibility, provided the architecture does not make later compiler-integrated analysis impossible.

Do not introduce a large dependency stack without clear value.

---

# Testing philosophy

Tests should establish semantic value, not merely line coverage.

Required categories for this foundation include:

```text
manifest validation
analyzer recognition
false-positive containment
classification output
contract registry validation
planner determinism
claim-gate enforcement
evidence serialization
CLI smoke behavior
fixture regression
```

Where possible, include golden deterministic output.

A change that modifies analysis output should make the difference obvious in review.

---

# Determinism

X-REF is intended for large agentic workflows.

Nondeterministic project state is poisonous to that goal.

Prefer:

```text
stable ordering
stable IDs
canonical serialization
repeatable analyzer output
explicit source revisions
exact commands
machine-readable evidence
```

The same source revision analyzed twice under the same X-REF version should produce the same static inventory unless intentionally configured otherwise.

---

# Human judgment boundary

X-REF is not intended to remove humans from kernel architecture design.

It is intended to make human judgment rarer and higher leverage.

The ideal state is:

```text
agents handle thousands of mechanical discoveries and migrations
humans handle dozens of genuine architecture decisions
```

When the system cannot establish a semantic mapping confidently, surface the decision.

A useful output is:

```text
HUMAN DESIGN QUESTION

Source behavior:
    x86 kernel uses feature X

Observed purpose:
    likely Y

Target choices:
    A
    B
    C

Evidence missing:
    Z
```

That is far better than inventing an answer.

---

# No fake success

Do not create placeholders that return success merely to make the target advance.

Do not silently stub architecture behavior.

Unsupported operations must be explicit.

Unknowns must remain unknown.

A target kernel that reaches a later boot line by violating the source semantics is not progress.

X-REF's reputation should eventually rest on this:

> When it says a migration step is proved, there is inspectable evidence behind the statement.

Trust permits aggressive automation.

---

# Scope control

This foundation task should prioritize the following order:

```text
1. coherent project structure
2. validated manifest/state model
3. static architecture-debt analyzer
4. structured findings/classification
5. semantic contract registry
6. deterministic port planner
7. evidence/claim model
8. CLI
9. fixtures/tests
10. documentation generated or updated from actual implementation
```

Do not spend the majority of effort on:

```text
UI
web dashboards
branding
automated code rewriting
LLM wrappers
remote orchestration
giant architecture databases
full compiler frontends
QEMU integration before the core project model exists
```

Those can come after the substrate is real.

---

# Expected initial deliverable

At the end of this foundation pass, a developer should be able to point X-REF at a small x86-oriented C/C++ kernel tree and perform something like:

```text
$ xref init ./fixture-x86-kernel --source x86_64 --target riscv64
Created .xref/port.yaml

$ xref analyze
Architecture dependencies: 37
  DIRECT:      14
  STRUCTURAL:   5
  ORDERING:     4
  PLATFORM:     7
  ABI:          3
  UNKNOWN:      4

Critical families:
  address-space
  interrupt
  context
  ordering

$ xref plan
Port readiness: 18%

Batch 001:
  isolate address-space activation
  contract: XREF-MM-001
  required source proof: source boot fixture

Batch 002:
  audit scheduler publication ordering
  classification: ORDERING
  human review: required

$ xref status
Highest proved level: L0 ANALYZED
Forbidden claims:
  RV64 boots
  target equivalent
  portable
```

The exact output format may differ.

The important result is that X-REF has become a **real executable porting framework** rather than documentation describing a future one.

---

# Stretch goal

If the core foundation is complete, tested, and coherent, begin an **adapter/probe interface** that would allow X-REF to ingest architecture knowledge from existing projects such as Z-REF without tightly coupling the repositories.

The desired relationship is:

```text
Z-REF
    reusable low-level mechanism/reference knowledge

X-REF
    consumes applicable knowledge as contracts, mappings,
    analyzer rules, diagnostics, and proof strategies
```

Do not copy large bodies of Z-REF code into X-REF merely to claim integration.

Define a clean ingestion format or adapter boundary first.

---

# Future vision

Build the foundation with this eventual scenario in mind:

```text
$ xref analyze ~/src/very-large-x86-kernel

4,218 architecture dependencies found
3,104 already covered by known X-REF contracts/patterns
  714 high-confidence mechanical migrations
  318 semantic migrations
   82 genuine design questions

Estimated reusable knowledge coverage: 73%
Suggested parallel agent tracks: 8
```

Then agents work against bounded contracts and evidence gates instead of wandering through the entire kernel independently.

Months or years later, the target boots.

And the next kernel begins with thousands of lessons already captured.

That is the future this foundation must enable.

---

# Definition of success for this task

Do not claim this foundation is complete until all of the following are true:

1. X-REF has executable tooling rather than only prose.
2. A port manifest can be created, loaded, validated, and deterministically serialized.
3. A kernel-like C/C++ fixture can be analyzed for x86 architecture debt.
4. Findings are structured and classified with confidence/provenance.
5. Semantic machine contracts have a validated registry representation.
6. A planner can convert findings/contracts into bounded ordered migration batches.
7. Evidence levels and claim gates are represented and enforced.
8. A CLI exposes the useful workflow.
9. Tests cover the main pipeline.
10. Documentation reflects what actually exists.
11. No result implies that an RV64 kernel was produced when no runtime proof exists.
12. The architecture clearly supports accumulating reusable knowledge from future real ports.

When these gates pass, report:

```text
what was built
commands to run it
tests executed
known limitations
exact next pressure
which parts directly support port-time reduction
```

---

# Final instruction

Do not build X-REF as an architecture translation novelty.

Build it as infrastructure intended to **compress years of kernel-porting labor**.

The ambition is not:

> "An AI can write RISC-V assembly."

The ambition is:

> **"A kernel architecture port no longer begins from zero knowledge."**

Every assumption discovered should become easier to discover again.

Every semantic contract proved should become reusable.

Every x86 -> RV64 mismatch understood should become encoded knowledge.

Every successful port should make the next one faster.

If X-REF eventually cuts a ten-year migration into five years, that is enormous.

If accumulated knowledge and better agents push some classes of ports far below that, even better.

But earn the speed through architecture, evidence, reuse, and disciplined automation.

**Make porting acceleration the invariant around which the repository grows.**
