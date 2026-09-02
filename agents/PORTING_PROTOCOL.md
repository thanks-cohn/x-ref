# X-REF Agent Porting Protocol

This document defines how an agent should participate in an X-REF architecture port.

The objective is not to maximize changed lines. The objective is to convert hidden architecture assumptions into explicit portable semantics while preserving observable kernel behavior.

## Prime directive

**Never translate an architecture-specific mechanism before identifying the semantic requirement it serves.**

The source machine is evidence, not the specification.

## Working loop

For each bounded porting batch:

```text
1. Observe
2. Inventory
3. Classify
4. Contract
5. Adapt source
6. Prove source unchanged
7. Implement target
8. Prove target
9. Record evidence
10. Continue
```

A batch should be small enough that the first divergent fact can be isolated when it fails.

## 1. Observe

Start from a concrete pressure:

```text
kernel reaches paging initialization
kernel enters userspace
kernel schedules second task
kernel enables interrupts
kernel starts second CPU
kernel runs one userspace ELF
kernel mounts root filesystem
```

Do not begin from a vague mission such as "port memory management."

A pressure gives the work a measurable end state.

## 2. Inventory

Search the full source path involved in the pressure.

Record every dependency on:

- inline assembly
- `.S` / `.asm` files
- architecture intrinsics
- register names
- privileged operations
- page-table encoding
- interrupt vectors/controllers
- barriers and atomics
- CPU-local state
- I/O instructions
- calling convention assumptions
- stack-frame assumptions
- firmware/boot interfaces
- feature detection
- machine-specific constants

Do not assume a dependency is harmless because it appears in common code.

## 3. Classify

Each finding receives one classification:

```text
CONTRACT
    fundamental machine service required by the kernel

BACKEND
    implementation detail that belongs only to the source backend

ACCIDENTAL
    source-architecture behavior leaked into common logic

ABI
    calling convention / executable format / userspace interface issue

DEVICE
    hardware/platform dependency rather than ISA dependency

UNKNOWN
    insufficient evidence; requires targeted investigation
```

Agents must prefer `UNKNOWN` over confident guessing.

## 4. Contract

For every `CONTRACT` item, either reuse an existing X-REF machine contract or propose the smallest semantic addition.

A proposal must include:

```text
intent
inputs
outputs
preconditions
postconditions
ordering
privilege
failure semantics
source behavior
proof strategy
target mapping
```

Never expose names like CR3, APIC, IDT, TSS, MSR, INVLPG, SATP, PLIC, or SFENCE.VMA in common interfaces unless the kernel truly requires that architecture-specific object.

## 5. Adapt source first

Before writing the target backend, route the working source architecture through the contract.

Example:

```text
before:
    scheduler -> write_cr3()

after:
    scheduler -> xref_address_space_activate()
                         |
                         v
                  x86_64 backend
                         |
                         v
                      CR3
```

The source kernel must still pass.

This stage is what transforms undocumented historical behavior into a reference implementation.

## 6. Prove source unchanged

Required evidence depends on the contract, but should include as many as practical:

- existing unit tests
- boot result
- deterministic trace comparison
- workload output comparison
- invariant checks
- mutation tests against the verifier

If source behavior changes, stop. Either the abstraction changed semantics or the previous semantics were accidental and must be explicitly adjudicated.

## 7. Implement target

Only after the source path is preserved should the agent implement the target architecture.

The target should use native mechanisms.

Do not reproduce the source architecture's implementation shape when the target architecture offers a different natural solution.

Example:

```text
semantic need:
    invalidate translations for an address space

x86-64:
    INVLPG / CR3 / PCID behavior as required

RV64:
    SFENCE.VMA scoped by address / ASID as required
```

## 8. Prove target

Compilation is evidence of syntax and linkage only.

Target completion requires runtime evidence appropriate to the mechanism.

Recommended hierarchy:

```text
unit
  -> backend conformance fixture
      -> QEMU machine fixture
          -> integrated kernel pressure
              -> source/target differential behavior
```

## 9. Record evidence

Every completed batch should produce a short machine-readable and human-readable record:

```text
pressure
contracts touched
source files changed
target files changed
source proof
target proof
known limitations
new accidental assumptions discovered
next causal blocker
```

Do not report "port complete" when the only passing gate is compilation.

## 10. Continue from the next blocker

The next batch is selected by the first real target failure, not by aesthetic preference.

```text
boot
 -> first trap failure
 -> repair trap contract
 -> first paging failure
 -> repair paging contract
 -> first scheduler failure
 -> repair scheduling boundary
 -> ...
```

This keeps the project pressure-driven and prevents speculative architecture work from outrunning evidence.

# Parallel agent model

Large kernels should be decomposed into bounded workstreams.

Example:

```text
Agent A: paging / translation
Agent B: interrupts / exceptions
Agent C: context / userspace entry
Agent D: atomics / memory ordering
Agent E: boot / firmware
Agent F: devices / MMIO
Agent G: conformance harness
Agent H: integration / first-divergence analysis
```

Parallel work is allowed only where ownership boundaries do not produce contradictory semantic contracts.

The integration agent is authoritative about the first target divergence.

# Required agent behaviors

An X-REF agent MUST:

- preserve existing source behavior before claiming portability
- distinguish ISA dependencies from platform/device dependencies
- inspect memory-order assumptions explicitly during x86 -> RV64 work
- prefer semantic interfaces over instruction-shaped interfaces
- keep architecture-specific code at backend edges
- record unsupported behavior instead of silently faking success
- add tests for new contracts
- make failures reproducible
- name the next causal blocker

An X-REF agent MUST NOT:

- replace x86 assembly with superficially similar RISC-V assembly without semantic analysis
- report success because the kernel compiles
- introduce a target-specific hack into common code merely to advance boot
- silently weaken protection, ordering, isolation, or privilege invariants
- emulate x86 concepts inside RISC-V when the kernel does not actually require those concepts
- rewrite unrelated kernel subsystems while performing an architecture port

# First-divergence discipline

When source and target behavior differ:

```text
observe failure
    |
    v
capture smallest useful trace
    |
    v
identify first divergent state
    |
    v
map divergence to contract or missing contract
    |
    v
repair semantic cause
    |
    v
rerun focused test
    |
    v
rerun integration pressure
```

Do not debug from the final crash backward when an earlier divergence can be captured.

# Port completion levels

X-REF uses progressive claims.

```text
L0 ANALYZED
architecture inventory exists

L1 ISOLATED
source machine dependencies route through contracts

L2 SOURCE-PROVED
source behavior preserved after isolation

L3 TARGET-BOOT
new architecture reaches kernel boot milestone

L4 TARGET-USER
new architecture enters and returns from userspace

L5 TARGET-WORKLOAD
real kernel workload runs

L6 DIFFERENTIAL
source and target pass shared semantic evidence

L7 PORTABLE
architecture boundary is reusable and documented
```

A project should state the highest level actually proved.

# Final principle

The apparent magic of X-REF should come from disciplined decomposition.

To the user it may look like:

> "Give an agent your x86 kernel and watch a RISC-V port appear."

Underneath, X-REF should make every step inspectable:

```text
assumption -> contract -> source proof -> target implementation -> target proof
```

That chain is the product.
