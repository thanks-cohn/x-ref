void console_putc(unsigned short port, char value) {
    outb(port, value);
}
