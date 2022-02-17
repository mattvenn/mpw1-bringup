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

    // turn on pin 8 as output
    li s3, 0x0180
    sw s3, IOCONF_OFS(9)

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

	li a0, 0x30000100

    /*
    register 0x30000100 definition
    | bits                               |
    | 31 : 24 | 23 : 16 | 15 : 8 | 7 : 0 |
    | led num | green   | red    | blue  |
    */

    // zero out the led reg
	li s0, (7 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (6 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (5 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (4 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (3 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (2 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (1 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)
	li s0, (0 << 24) + (0 << 16) + (0 << 8 ) + 0
	sw s0, 0(a0)


    // s2 is the reg used for what led to set
    // s3 is what gets written to led
    li s8, 0
    li s7, 0
    li s3, 0
init_val:
    // s1 is used for the RGB value
    li s1, 0
loop:
    // do this many nops before incrementing led value
    li s6, 300
    li s5, 0
inner:
    // this loop to slow things down enough to animate. 
    addi    s5, s5, 1
    nop
    ble s5, s6, inner

    // add 1 to s1
	addi    s1, s1, 1

    // if led value is 150, reset to 0
    li s3, 150 // compare reg
    bge s1, s3, init_val

    // shift 8 bits to R, store in s3
    slli s3,s1,8

    // add fixed 20 of blue (no shift needed as blue is bits 7:0)
    li s5, 20
    add s3, s3, s5

    // shift the led number in reg s7 by 24 bits and store in s2
    slli s2, s7, 24
    // add the led number (s2) and the rgb (s3) value, store in s4
    add s4, s3, s2

    // write to led, put what's in s4 into the memory address at a0 (at offset 0)
	sw s4, 0(a0)

    // increment led number every 10 iterations
    addi s8, s8, 1
    li s9, 10
    ble s8, s9, loop
    // otherwise add to led
    addi s7, s7, 3
    li s8, 0
	j loop

    // load a0 with nothing first to avoid mishaps when picorv32 crashes
	li a0, 0x00000000
	// Infinite loop
1:
	nop
	j 1b
