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

        li s3, 0x0001
        sw s3, IOCONF_OFS(14)
        li s3, 0x0006
        sw s3, IOCONF_OFS(15)
        li s3, 0x000c
        sw s3, IOCONF_OFS(16)
	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Enable project 1
	li a0, 0x30000000
	li s0, 1
	sw s0, 0(a0)

    // set an led: write to address h30000100
    // ws2812                proj_1 (.clk(proj1_clk), .reset(proj1_reset), .led_num(wbs_dat_i[31:24]), .rgb_data(wbs_dat_i[23:0]), .write(proj1_wb_update), .data(proj1_io_out[8]));

    // https://github.com/mattvenn/ws2812-core/tree/776a4d527ff8af7ac508a334bb1ef970df6f5848
	li a0, 0x30000100
	li s0, (7 << 24) + (255 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (6 << 24) + (0 << 16) + (255 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (5 << 24) + (0 << 16) + (0 << 8 ) + 255 
	sw s0, 0(a0)
	li s0, (4 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (3 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (2 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (1 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)

    li s0, 0
2:
	nop
	nop
	nop
	addi    s0, s0, 1
	sw s0, 0(a0)
	j 2b


    // load a0 with nothing first to avoid mishaps when picorv32 crashes
	li a0, 0x00000000
	// Infinite loop
1:
	nop
	j 1b
