CROSS ?= riscv64-unknown-elf-
CC = $(CROSS)gcc
OBJCOPY = $(CROSS)objcopy

CFLAGS=-march=rv32i -mabi=ilp32 -ffreestanding -nostartfiles --specs=nano.specs -I.

all: test-vdd-scan.bin

%.elf: %.S lnk-test.lds
	$(CC) $(CFLAGS) -Wl,-Bstatic,-T,lnk-test.lds,--strip-debug -o $@ $<

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@

clean:
	rm -f *.bin *.elf

.PHONY: clean
