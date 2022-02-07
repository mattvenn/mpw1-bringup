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
    li s3, 0x0180
    sw s3, IOCONF_OFS(9)

	li s3, 0x0600
	sw s3, IOCONF_OFS(10)

	li s3, 0x0c00
	sw s3, IOCONF_OFS(11)

	li s3, 0x1800
	sw s3, IOCONF_OFS(12)

	li s3, 0x1000
	sw s3, IOCONF_OFS(13)

    li s3, 0x1001
    sw s3, IOCONF_OFS(14)

//    li s3, 0x0002
    li s3, 0x0000
    sw s3, IOCONF_OFS(15)

    li s3, 0x0003
	sw s3, IOCONF_OFS(16)

	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Enable project 0
    // enabled by default

    // set a new compare
	li a0, 0x30000200
	li s0, 2000000
	sw s0, 0(a0)

	li a0, 0x00000000
	// Infinite loop
1:
	nop
	j 1b
