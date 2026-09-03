# X-REF

**Agent-assisted kernel architecture porting.**

> Give X-REF an x86-64 kernel. Let agents expose what the kernel assumes about the machine, replace those assumptions with explicit semantic contracts, implement the same contracts for RISC-V, and prove that the new kernel still behaves like the old one.

X-REF is an experiment in making kernel ports **mechanical, inspectable, parallelizable, and provable**.

The dream is simple:

```text
                 YOUR EXISTING KERNEL
                         x86-64
                            |
                            v
                    X-REF ANALYSIS
                            |
             architecture assumptions found
                            |
                            v
                   MACHINE CONTRACTS
                            |
              +-------------+-------------+
              |                           |
              v                           v
           x86-64                       RISC-V
        reference path                target path
              |                           |
              +-------------+-------------+
                            |
                            v
                 DIFFERENTIAL EVIDENCE
                            |
                            v
                 WORKING RISC-V KERNEL
```

Not a rewrite. Not an emulator. Not a line-by-line instruction translator.

**A porting substrate.**

X-REF treats the existing kernel as a body of behavior worth preserving and the source architecture as a collection of assumptions that can be discovered, named, isolated, replaced, and tested.

The first mission is deliberately concrete:

> **x86-64 kernel -> working RV64 kernel, with agents doing as much of the migration work as can be made safe and reproducible.**

## Why this should exist

A large kernel can contain years of architecture knowledge scattered across paging code, interrupt setup, atomics, context switching, boot code, CPU-local state, device access, memory ordering, assembly, compiler intrinsics, and accidental assumptions that nobody wrote down because they were always true on the original machine.

That makes a conventional architecture port expensive for a strange reason: much of the work is not inventing new kernel behavior. It is **rediscovering what the old kernel already meant**.

X-REF attacks that rediscovery problem.

Agents are unusually good at wide codebase archaeology when they are given a disciplined target. They can search thousands of files, classify direct and indirect machine dependencies, propose replacements, generate focused tests, compare source and target behavior, and work in parallel. But without a framework, they can also produce a mountain of plausible-looking code whose correctness is impossible to establish.

X-REF exists to provide that framework.

## The central rule

**Port semantics, not instructions.**

Do not translate:

```c
write_cr3(root);
```

into a RISC-V imitation of `write_cr3`.

First discover what the kernel actually needs:

```c
xref_address_space_activate(root);
```

Then satisfy that operation independently:

```text
x86-64 implementation
    CR3 / PCID / INVLPG / architectural ordering

RV64 implementation
    SATP / ASID / SFENCE.VMA / architectural ordering
```

The contract is the durable artifact. The instruction sequence is merely one machine's implementation.

## What X-REF does

An X-REF port proceeds through six pressures.

### 1. Discover

Scan the source kernel for architecture debt:

- inline and external assembly
- privileged instructions
- architecture-specific intrinsics
- page-table formats
- interrupt-controller assumptions
- context/register layouts
- atomics and memory-order assumptions
- CPU-local storage
- port I/O and MMIO
- boot protocol dependencies
- timer and clock behavior
- cache and TLB management
- ABI and calling-convention assumptions
- device-model assumptions

The output is not just a list of files. It is a **port inventory**.

### 2. Classify

Every dependency is assigned to a semantic family:

```text
boot
cpu
memory
address-space
interrupt
exception
context
atomic
ordering
timer
smp
io
firmware
device
userspace-entry
```

X-REF distinguishes three important cases:

1. **Fundamental kernel requirement**: belongs behind a machine contract.
2. **Source-machine implementation detail**: stays in the x86-64 backend.
3. **Accidental architecture dependency**: should be removed rather than reproduced.

### 3. Contract

Turn each fundamental requirement into a small, architecture-neutral contract.

A contract answers:

- What operation does the kernel need?
- What state may it observe or modify?
- What ordering is required?
- What must be true when it returns?
- What failure modes exist?
- Which source-architecture behavior is intentional?
- How will the behavior be tested on both architectures?

See [`contracts/MACHINE_CONTRACT.md`](contracts/MACHINE_CONTRACT.md).

### 4. Preserve

Move the existing x86-64 implementation behind the new contract **without changing behavior**.

This is a non-negotiable stage.

Before RISC-V exists, the x86-64 kernel should still boot and pass its existing tests through the X-REF boundary. That converts the original machine implementation into an executable reference.

### 5. Implement

Agents implement the same semantic contract for RV64.

The target backend is expected to use native RISC-V concepts, not preserve x86 vocabulary. For example:

```text
x86-64                     RV64
------------------------------------------------
CR3                  ->    SATP
4/5-level x86 PT     ->    Sv39/Sv48
INVLPG               ->    SFENCE.VMA
APIC                 ->    AIA/PLIC where applicable
port I/O             ->    MMIO / platform mechanism
x86 privilege        ->    M/S/U privilege model
TSO assumptions      ->    explicit RVWMO-safe ordering
```

The mapping document begins at [`mappings/x86_64-riscv64.md`](mappings/x86_64-riscv64.md).

### 6. Prove

A target implementation does not pass because it compiles.

It passes when evidence shows that the contract holds.

X-REF encourages:

- unit tests
- architecture conformance tests
- QEMU boot tests
- deterministic machine traces
- source/target differential tests
- mutation tests for the verifier itself
- invariant checks
- W^X and privilege checks
- SMP stress where relevant
- preserved source-architecture regressions

The final product of a port is therefore not merely `arch/riscv64/`.

It is:

```text
implementation + contracts + evidence + reproducible procedure
```

## The agentic porting loop

The intended workflow is deliberately repetitive:

```text
observe source behavior
        |
        v
discover architecture dependency
        |
        v
name the semantic requirement
        |
        v
write/extend contract
        |
        v
adapt x86 implementation behind contract
        |
        v
prove x86 behavior unchanged
        |
        v
implement RV64 behavior
        |
        v
run conformance + differential evidence
        |
        +---- failure ----> isolate first divergent fact ----+
        |                                                   |
        +---------------------------------------------------+
        |
       pass
        |
        v
commit one proven migration step
```

That loop is described for agents in [`agents/PORTING_PROTOCOL.md`](agents/PORTING_PROTOCOL.md).

## The dream workflow

The long-term interface should feel closer to this:

```text
$ xref analyze ../my-kernel --source x86_64 --target riscv64

Architecture inventory
----------------------
Direct machine dependencies:      4,217
Already isolated:                 2,904
Mechanical candidates:              781
Semantic migrations required:       468
Human design questions:               64

Port readiness: 68%

Top blockers
------------
1. address-space activation
2. interrupt routing
3. context restore
4. x86 TSO-dependent lock path
5. APIC timer abstraction

Suggested agent batches: 9
```

Then:

```text
$ xref port --target riscv64

[1/9] address-space contracts ........ PASS
[2/9] user-entry contracts ........... PASS
[3/9] timer contracts ................ PASS
[4/9] ordering audit ................. PASS
...

x86 regression:     PASS
RV64 conformance:   PASS
RV64 boot:          PASS
```

The phrase **"give an agent your x86 kernel and get a working RISC-V clone"** is the destination. X-REF exists to turn that apparent magic into a sequence of explicit transformations whose evidence can be inspected.

## Repository layout

```text
x-ref/
├── README.md
├── agents/
│   └── PORTING_PROTOCOL.md
├── contracts/
│   └── MACHINE_CONTRACT.md
├── include/
│   └── xref/
│       └── machine.h
├── mappings/
│   └── x86_64-riscv64.md
├── schemas/
│   └── port-manifest.example.yaml
└── docs/
    └── ARCHITECTURE.md
```

This repository begins as a specification and porting framework. Implementations and automation should grow only where they strengthen the central contract/evidence model.

The first implementation foundation is now available as a small Python CLI.
It validates durable port manifests, inventories and conservatively classifies
C/C++ architecture debt, exposes a semantic contract registry, and suggests
deterministic bounded review batches. See [`docs/TOOLING.md`](docs/TOOLING.md)
for commands, limitations, and the next causal milestone.

## Relationship to Z-REF

X-REF is spiritually downstream of **Z-REF**.

Z-REF asks:

> Can a low-level mechanism be reduced to a small, reusable, documented, testable reference?

X-REF asks the next question:

> If those mechanisms and contracts are explicit, can agents use them to move an entire kernel from one architecture to another dramatically faster than a traditional port?

Z-REF supplies reusable knowledge and proof habits. X-REF applies those habits to architecture migration at kernel scale.

## Initial target

The first proving pair is:

```text
source: x86-64
target: RISC-V RV64
```

The framework should not encode assumptions that make ARM64, WASM-hosted machines, hypervisor personalities, or future architectures impossible. But they are not the first pressure.

First, prove the idea on the port that matters.

## Success criteria

X-REF succeeds when a kernel project can demonstrate all of the following:

1. Its architecture-dependent behavior is represented by explicit machine contracts.
2. The original x86-64 kernel still passes through those contracts.
3. The same kernel core builds against an RV64 machine implementation.
4. The RV64 kernel boots and executes real workloads.
5. Source and target behavior can be compared mechanically.
6. The evidence is reproducible by someone who did not perform the port.
7. The amount of architecture-specific reasoning required for the next kernel is lower because X-REF captured what was learned.

The last point is the real prize.

Every successful port should make the next port cheaper.

## What X-REF is not

X-REF is not:

- an x86 emulator
- a binary translator
- a transpiler that blindly rewrites assembly
- a promise that arbitrary kernels can be ported without architectural judgment
- a replacement for understanding the target ISA
- a compatibility layer that forces RISC-V to pretend to be x86

The system should automate what can be made mechanical and make the remaining judgment **obvious, bounded, and reviewable**.

## The idea in one sentence

**X-REF turns kernel architecture ports from heroic archaeology into contract-driven migration.**

Give it the old machine. Give it the new machine. Preserve what the kernel means.
