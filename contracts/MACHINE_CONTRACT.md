# X-REF Machine Contract

The machine contract is the heart of X-REF.

It is the boundary between **what the kernel means** and **how one architecture happens to implement it**.

A valid X-REF contract must be semantic. It must not leak source-architecture vocabulary into the common kernel merely because the original implementation used that vocabulary.

## Contract rule

Bad:

```c
xref_write_cr3(root);
```

Good:

```c
xref_address_space_activate(root);
```

Bad:

```c
xref_invlpg(address);
```

Good:

```c
xref_translation_invalidate(address, scope);
```

Bad:

```c
xref_apic_send_ipi(cpu, vector);
```

Good:

```c
xref_interrupt_send(cpu, reason);
```

The source backend may use CR3, INVLPG, APIC, PCID, IST, XSAVE, or any other x86 mechanism. The RV64 backend may use SATP, SFENCE.VMA, SBI, AIA, PLIC, or other RISC-V mechanisms. Those names belong at the backend edge.

## Required contract record

Every machine contract should answer the following.

```text
id
name
semantic family
caller
inputs
outputs
preconditions
postconditions
ordering guarantees
privilege assumptions
failure modes
source implementation
source evidence
target implementation
target evidence
known non-equivalences
```

## Semantic families

Initial families:

```text
boot
cpu
memory
address-space
translation
context
userspace-entry
exception
interrupt
timer
atomic
ordering
smp
cpu-local
firmware
io
device
power
```

New families should be introduced only when a real kernel pressure cannot be expressed cleanly by the existing vocabulary.

## Example contract: address-space activation

### Identity

```text
id: XREF-MM-001
name: address-space-activate
family: address-space
```

### Intent

Make a supplied kernel address-space object the active translation context for the current hardware thread.

### Preconditions

- The address-space root is valid according to the active backend.
- Required kernel mappings are present.
- The caller is executing at sufficient privilege.
- The object remains alive for the duration of activation.

### Postconditions

- Subsequent userspace virtual-memory translations are derived from the supplied address space.
- Required kernel mappings remain accessible.
- No stale translation may permit access forbidden by the new address space.
- Required ordering rules have been satisfied before control returns.

### Source implementation example

```text
x86-64:
    prepare CR3 value
    preserve/choose PCID according to policy
    activate root
    invalidate as required by architecture and generation rules
```

### Target implementation example

```text
RV64:
    prepare SATP value
    preserve/choose ASID according to policy
    activate root
    issue required SFENCE.VMA operations
```

### Evidence

- Source kernel boots through contract.
- Source regression suite remains unchanged.
- Target conformance fixture switches between two address spaces with mutually exclusive mappings.
- Negative fixture proves stale translation cannot cross the boundary.
- Repeated activation remains deterministic.

## Example contract: context switch

A context-switch contract does not require the register sets to be identical.

It requires preservation of the **kernel-visible execution state**.

```text
XREF-CPU-004 context-switch

Given:
    outgoing execution context A
    incoming execution context B

After completion:
    A contains all state required for a later legal resume
    execution continues as B
    B observes the register/stack/TLS/privilege state promised by the kernel ABI
    machine-local transient state cannot leak across the switch where isolation is required
```

The x86 backend may save one set of architectural state. RV64 may save another. The common contract names only what the kernel actually relies on.

## Memory ordering is a first-class contract concern

One of the most dangerous x86 -> RISC-V porting errors is accidental dependence on x86 memory ordering.

X-REF must never assume that code which behaved correctly under x86 TSO is automatically correct under RVWMO.

Every synchronization contract must state its ordering requirement explicitly.

Examples:

```text
relaxed
acquire
release
acquire-release
sequentially-consistent
architecture-specific stronger invariant
```

When an agent finds synchronization whose correctness depends on undocumented x86 ordering, it must classify it as an **accidental architecture dependency** and repair the common kernel semantics before implementing the RV64 path.

## Contract maturity

Each contract carries a maturity state:

```text
DISCOVERED
    requirement observed but not yet normalized

DEFINED
    semantic contract written

SOURCE_ADAPTED
    source architecture routes through contract

SOURCE_PROVED
    source behavior preserved by evidence

TARGET_IMPLEMENTED
    target backend exists

TARGET_PROVED
    target evidence passes

PORTABLE
    contract has passed source + target conformance and is reusable
```

A contract is not considered portable merely because both backends compile.

## Contract design test

Before accepting a contract, ask:

> If ARM64 were added tomorrow, would the contract still make sense without pretending ARM64 is x86 or RISC-V?

If the answer is no, the abstraction is probably too low-level or named incorrectly.

## Machine capabilities

Not every platform can implement every optional facility. X-REF therefore distinguishes **required semantics** from **capabilities**.

Examples:

```text
XREF_CAP_SMP
XREF_CAP_USER_MODE
XREF_CAP_ADDRESS_SPACE_TAGS
XREF_CAP_HARDWARE_VIRTUALIZATION
XREF_CAP_VECTOR_STATE
XREF_CAP_PRECISE_TIMER
```

Capability discovery must not become an excuse for silent semantic degradation. If a kernel requires a property, absence of that property should fail loudly during configuration or boot.

## Evidence is part of the contract

A contract without evidence is documentation.

A contract with a source adapter, target adapter, and reproducible conformance evidence is a portability primitive.

That distinction is central to X-REF.
