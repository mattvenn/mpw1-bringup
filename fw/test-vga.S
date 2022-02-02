/*
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

	// Load config
	li s3, 0x1800
	sw s3, IOCONF_OFS(12)

	li s3, 0x1000
	sw s3, IOCONF_OFS(13)

	li s3, 0x0003
	sw s3, IOCONF_OFS(14)

	li s3, 0x0003
	sw s3, IOCONF_OFS(15)
	li s3, 0x0003
	sw s3, IOCONF_OFS(16)
	li s3, 0x0003
	sw s3, IOCONF_OFS(17)
	li s3, 0x000c
	sw s3, IOCONF_OFS(18)
	li s3, 0x0018
	sw s3, IOCONF_OFS(19)
	li s3, 0x0030
	sw s3, IOCONF_OFS(20)

	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Enable project 2
	li a0, 0x30000000
	li s0, 2
	sw s0, 0(a0)


    // set the oeb reg to get inputs working
	li s0, (1 << 8) + (1 << 9) + (1 << 10)
	sw s0, 4(a0)

	li a0, 0x00000000
	// Infinite loop
1:
	nop
	j 1b
