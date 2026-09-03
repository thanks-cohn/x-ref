/* This is architecture-specific and correctly contained in its backend. */
void disable_interrupts(void) {
    asm volatile("cli" ::: "memory");
}
