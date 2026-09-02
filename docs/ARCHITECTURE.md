# X-REF Architecture

X-REF is built around one architectural separation:

```text
                  PORTABLE KERNEL CORE
                         |
                  X-REF CONTRACTS
                         |
          +--------------+--------------+
          |                             |
      SOURCE BACKEND                 TARGET BACKEND
         x86-64                         RV64
          |                             |
     source machine                  target machine
```

The common kernel should express **requirements**.

The backends should express **mechanisms**.

The porting system exists to discover where an existing kernel violated that separation and repair it incrementally without losing working behavior.

## Components

X-REF has five conceptual components.

### 1. Analyzer

The analyzer discovers architecture coupling.

Inputs:

```text
kernel source tree
source architecture
build metadata
test commands
known boot/run commands
```

Outputs:

```text
architecture dependency inventory
classification by semantic family
source-machine hotspots
ordering-risk sites
candidate contract boundaries
port readiness score
suggested bounded agent batches
```

The analyzer should eventually combine lexical, compiler, build-graph, and runtime evidence.

Static scanning alone is insufficient because some architecture assumptions are indirect.

### 2. Machine contract layer

The contract layer contains architecture-neutral semantic operations.

Examples:

```text
address-space activation
translation invalidation
context switching
userspace entry
interrupt delivery
timer programming
CPU-local identity
memory ordering
```

Contracts should remain small enough to reason about independently and broad enough that adding a third architecture does not require renaming the API around the first two.

### 3. Architecture backends

Each backend satisfies machine contracts using native mechanisms.

```text
backend/x86_64
backend/riscv64
future: backend/arm64
future: backend/wasm-host
```

Backend-private interfaces are allowed.

A backend-private operation becomes a common contract only when the portable kernel genuinely depends on its semantics.

### 4. Evidence engine

The evidence engine answers the question that ordinary source translation cannot:

> Did the port preserve what mattered?

Evidence should be layered:

```text
unit tests
    |
backend conformance
    |
machine/QEMU tests
    |
full-kernel workload
    |
source-target differential evidence
```

Evidence artifacts should be reproducible and tied to exact source revisions.

### 5. Agent orchestrator

The orchestrator decomposes a port into bounded causal work.

It should know:

- current source revision
- current target revision
- contract maturity
- first target divergence
- current pressure
- dependency graph between workstreams
- evidence state
- forbidden claims

The orchestrator should optimize for **verified semantic progress**, not number of generated patches.

## Architecture debt model

X-REF uses the term **architecture debt** for source code whose correctness or meaning depends on properties of one machine.

Architecture debt is not automatically bad code. A kernel written for x86 should use x86.

It becomes porting debt when architecture-specific knowledge is spread through common logic in a form that cannot be isolated or reasoned about.

X-REF divides architecture debt into:

```text
DIRECT
    explicit assembly/register/intrinsic dependency

STRUCTURAL
    data structures mirror machine formats

BEHAVIORAL
    logic depends on machine semantics without naming them

ORDERING
    synchronization depends on source memory model

PLATFORM
    board/firmware/device assumption mistaken for ISA requirement

ABI
    calling convention, executable, userspace, or toolchain dependency

ACCIDENTAL
    source behavior that should not survive the port
```

The analyzer and agents should make this debt visible before rewriting it.

## Portability gradient

X-REF does not require a kernel to become architecture-neutral all at once.

Portability is progressive:

```text
architecture-specific kernel
        |
        v
inventory exists
        |
        v
critical assumptions isolated
        |
        v
source backend passes contracts
        |
        v
target backend begins boot
        |
        v
shared workloads pass
        |
        v
portable architecture boundary
```

This allows large kernels to remain useful throughout the migration.

## First proving architecture pair

The initial pair is:

```text
x86-64 -> RISC-V RV64
```

This pair is deliberately valuable because the architectures differ in ways that expose weak abstractions:

- memory ordering
- interrupt models
- privilege structures
- page-table formats
- firmware conventions
- I/O conventions
- CPU discovery
- virtualization facilities

A framework that survives this gap is more meaningful than one proven only across closely related platforms.

## Source preservation as an architectural feature

A conventional port often creates the target architecture beside the source architecture and slowly duplicates source behavior.

X-REF requires an extra step:

```text
working x86 code
      |
      v
semantic contract introduced
      |
      v
x86 code adapted behind contract
      |
      v
x86 behavior proved unchanged
      |
      v
RV64 implementation begins
```

This makes the source architecture an executable oracle and greatly reduces ambiguity during target debugging.

## Differential semantics

Not every machine observation should be identical.

For example, source and target will naturally differ in:

```text
register values
interrupt vector numbers
page-table encoding
firmware structures
cycle counts
physical addresses
```

Differential evidence therefore compares **normalized semantic events** where possible.

Example:

```text
SOURCE TRACE
address-space.activate pid=4 generation=9
mapping.add pid=4 va=0x400000 perms=RXU
userspace.enter pid=4 entry=0x401000
syscall.enter class=write
syscall.complete result=12

TARGET TRACE
address-space.activate pid=4 generation=9
mapping.add pid=4 va=0x400000 perms=RXU
userspace.enter pid=4 entry=0x401000
syscall.enter class=write
syscall.complete result=12
```

The underlying CR3/SATP operations do not need to match. The kernel-visible meaning does.

## Learning across ports

X-REF should accumulate reusable port knowledge.

A successful migration teaches the framework:

```text
architecture pattern
    -> semantic classification
    -> contract
    -> source adaptation shape
    -> target implementation pattern
    -> proof strategy
    -> known failure signatures
```

The long-term objective is that the tenth kernel port requires less novel reasoning than the first.

This is where X-REF becomes more than a portability library.

It becomes a **corpus of proven kernel migration knowledge for agents**.

## Future extensions

After x86-64 -> RV64 is proved, natural extensions include:

```text
ARM64 backend
WASM-hosted machine backend
hypervisor-backed machine personality
port analysis across C, C++, Zig, and Rust kernels
compiler-assisted architecture-debt extraction
QEMU trace adapters
formalized contract schemas
automatic source/target differential harnesses
```

These are future pressures, not reasons to complicate the first contract set.

## Architectural test

For every new feature, ask:

> Does this help us take a real kernel whose machine assumptions are currently implicit and move it to another architecture with less rediscovery, less guesswork, and stronger evidence?

If not, it probably does not belong in X-REF yet.
