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

	//
	// challenge proj_6 (.uart(proj6_io_in[8]), .clk_10(proj6_clk), .led_green(proj6_io_out[9]), .led_red(proj6_io_out[10]));
	// 8 input
	// 9 output
	// 10 output

	// Load config

	li s3, 0x0040
	sw s3, IOCONF_OFS(9)
	li s3, 0x0600
	sw s3, IOCONF_OFS(10)
	li s3, 0x0c00
	sw s3, IOCONF_OFS(11)

	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Enable project 6
	li a0, 0x30000000
	li s0, 6
	sw s0, 0(a0)


	li a0, 0x00000000
	// Infinite loop
1:
	nop
	j 1b
