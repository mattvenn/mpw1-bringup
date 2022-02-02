/*
 * test-vdd-scan.S
 *
 * Firmware for VDD scanning to find dies and VDD ranges that have
 * a chance of working "well enough"
 *
 * Copyright (C) 2021-2022  Sylvain Munaut <tnt@246tNt.com>
 * SPDX-License-Identifier: MIT
 */

#define IOCONF_BASE	0x26000000
#define IOCONF_OFS(x)	(0x20 + 4 * (x))(a0)

	.section .text.start
	.global _start
_start:
	// Set configuration
	li a0, IOCONF_BASE

	// Clear all registers
	li a1, 0x26000020
	li a2, 0x260000b8

1:
	nop
	sw zero, 0(a1)
	addi    a1, a1, 4
	bne	a1, a2, 1b

	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Infinite loop
	// (with nops to distinguish read burst length
	//  from the loop above)
1:
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	j 1b
