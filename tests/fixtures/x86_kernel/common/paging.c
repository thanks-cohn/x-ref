#include <stdint.h>

/* Deliberately leaked x86 mechanism: analyzer must propose semantic review. */
void activate_page_map(uint64_t root) {
    asm volatile("mov %0, %%cr3" : : "r"(root) : "memory");
}

/* Deliberately documented ordering debt hidden by the source memory model. */
void publish_ready(volatile int *ready) {
    *ready = 1; /* XREF_ORDERING_REVIEW: TSO-dependent publication */
}
