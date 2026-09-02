#ifndef XREF_MACHINE_H
#define XREF_MACHINE_H

/*
 * X-REF machine contract skeleton.
 *
 * This header intentionally names semantic kernel requirements rather than
 * source-architecture instructions. Architecture backends satisfy these
 * contracts independently.
 *
 * It is an initial framework, not a frozen ABI.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint64_t xref_cpu_id_t;
typedef uint64_t xref_phys_addr_t;
typedef uint64_t xref_virt_addr_t;
typedef uint64_t xref_address_space_id_t;
typedef uint64_t xref_ticks_t;

enum xref_status {
    XREF_OK = 0,
    XREF_UNSUPPORTED,
    XREF_INVALID,
    XREF_DENIED,
    XREF_BUSY,
    XREF_FAILED
};

enum xref_capability {
    XREF_CAP_USER_MODE                 = 1ull << 0,
    XREF_CAP_SMP                       = 1ull << 1,
    XREF_CAP_ADDRESS_SPACE_TAGS        = 1ull << 2,
    XREF_CAP_HARDWARE_VIRTUALIZATION   = 1ull << 3,
    XREF_CAP_VECTOR_STATE              = 1ull << 4,
    XREF_CAP_PRECISE_TIMER             = 1ull << 5
};

enum xref_memory_order {
    XREF_ORDER_RELAXED = 0,
    XREF_ORDER_ACQUIRE,
    XREF_ORDER_RELEASE,
    XREF_ORDER_ACQ_REL,
    XREF_ORDER_SEQ_CST
};

enum xref_translation_scope {
    XREF_TRANSLATION_ADDRESS = 0,
    XREF_TRANSLATION_ADDRESS_SPACE,
    XREF_TRANSLATION_GLOBAL
};

struct xref_address_space {
    xref_phys_addr_t root;
    xref_address_space_id_t id;
    uint64_t backend_flags;
};

struct xref_user_context {
    xref_virt_addr_t instruction_pointer;
    xref_virt_addr_t stack_pointer;
    xref_virt_addr_t thread_pointer;
    uint64_t opaque[32];
};

struct xref_kernel_context {
    uint64_t opaque[40];
};

struct xref_interrupt_reason {
    uint32_t class_id;
    uint32_t reason_id;
    uint64_t payload;
};

struct xref_machine_info {
    const char *architecture;
    const char *platform;
    uint64_t capabilities;
    uint32_t hardware_threads;
    uint32_t page_shift;
};

/* Discovery */
const struct xref_machine_info *xref_machine_info(void);
bool xref_machine_has(enum xref_capability capability);

/* CPU / execution */
xref_cpu_id_t xref_cpu_current(void);
void xref_cpu_relax(void);
void xref_cpu_halt(void);

/* Interrupt state */
void xref_interrupt_disable(void);
void xref_interrupt_enable(void);
bool xref_interrupt_enabled(void);

enum xref_status xref_interrupt_send(
    xref_cpu_id_t cpu,
    struct xref_interrupt_reason reason);

/* Address spaces and translation */
enum xref_status xref_address_space_activate(
    const struct xref_address_space *space);

enum xref_status xref_translation_invalidate(
    const struct xref_address_space *space,
    xref_virt_addr_t address,
    enum xref_translation_scope scope);

/* Execution context */
void xref_context_switch(
    struct xref_kernel_context *outgoing,
    const struct xref_kernel_context *incoming);

void xref_userspace_enter(const struct xref_user_context *context);

/* Time */
xref_ticks_t xref_timer_now(void);
enum xref_status xref_timer_program(xref_ticks_t deadline);

/* Ordering */
void xref_memory_fence(enum xref_memory_order order);

/* Platform I/O primitives. Device policy belongs above this layer. */
enum xref_status xref_mmio_read32(
    xref_phys_addr_t address,
    uint32_t *value);

enum xref_status xref_mmio_write32(
    xref_phys_addr_t address,
    uint32_t value);

/*
 * Architecture backends may expose additional private helpers internally.
 * They must not become common-kernel dependencies without first being
 * promoted to a semantic X-REF contract.
 */

#ifdef __cplusplus
}
#endif

#endif /* XREF_MACHINE_H */
