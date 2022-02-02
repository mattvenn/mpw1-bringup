/*
 * test-io-mapper.S
 *
 * Firmware for IO config bit mapping to find out where bits ends up
 * in the final shift register
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

	// Load each configured register
#ifdef IOCONF_VAL_0
	li s0, IOCONF_VAL_0
	sw s0, IOCONF_OFS(0)
#endif

#ifdef IOCONF_VAL_1
	li s0, IOCONF_VAL_1
	sw s0, IOCONF_OFS(1)
#endif

#ifdef IOCONF_VAL_2
	li s0, IOCONF_VAL_2
	sw s0, IOCONF_OFS(2)
#endif

#ifdef IOCONF_VAL_3
	li s0, IOCONF_VAL_3
	sw s0, IOCONF_OFS(3)
#endif

#ifdef IOCONF_VAL_4
	li s0, IOCONF_VAL_4
	sw s0, IOCONF_OFS(4)
#endif

#ifdef IOCONF_VAL_5
	li s0, IOCONF_VAL_5
	sw s0, IOCONF_OFS(5)
#endif

#ifdef IOCONF_VAL_6
	li s0, IOCONF_VAL_6
	sw s0, IOCONF_OFS(6)
#endif

#ifdef IOCONF_VAL_7
	li s0, IOCONF_VAL_7
	sw s0, IOCONF_OFS(7)
#endif

#ifdef IOCONF_VAL_8
	li s0, IOCONF_VAL_8
	sw s0, IOCONF_OFS(8)
#endif

#ifdef IOCONF_VAL_9
	li s0, IOCONF_VAL_9
	sw s0, IOCONF_OFS(9)
#endif

#ifdef IOCONF_VAL_10
	li s0, IOCONF_VAL_10
	sw s0, IOCONF_OFS(10)
#endif

#ifdef IOCONF_VAL_11
	li s0, IOCONF_VAL_11
	sw s0, IOCONF_OFS(11)
#endif

#ifdef IOCONF_VAL_12
	li s0, IOCONF_VAL_12
	sw s0, IOCONF_OFS(12)
#endif

#ifdef IOCONF_VAL_13
	li s0, IOCONF_VAL_13
	sw s0, IOCONF_OFS(13)
#endif

#ifdef IOCONF_VAL_14
	li s0, IOCONF_VAL_14
	sw s0, IOCONF_OFS(14)
#endif

#ifdef IOCONF_VAL_15
	li s0, IOCONF_VAL_15
	sw s0, IOCONF_OFS(15)
#endif

#ifdef IOCONF_VAL_16
	li s0, IOCONF_VAL_16
	sw s0, IOCONF_OFS(16)
#endif

#ifdef IOCONF_VAL_17
	li s0, IOCONF_VAL_17
	sw s0, IOCONF_OFS(17)
#endif

#ifdef IOCONF_VAL_18
	li s0, IOCONF_VAL_18
	sw s0, IOCONF_OFS(18)
#endif

#ifdef IOCONF_VAL_19
	li s0, IOCONF_VAL_19
	sw s0, IOCONF_OFS(19)
#endif

#ifdef IOCONF_VAL_20
	li s0, IOCONF_VAL_20
	sw s0, IOCONF_OFS(20)
#endif

#ifdef IOCONF_VAL_21
	li s0, IOCONF_VAL_21
	sw s0, IOCONF_OFS(21)
#endif

#ifdef IOCONF_VAL_22
	li s0, IOCONF_VAL_22
	sw s0, IOCONF_OFS(22)
#endif

#ifdef IOCONF_VAL_23
	li s0, IOCONF_VAL_23
	sw s0, IOCONF_OFS(23)
#endif

#ifdef IOCONF_VAL_24
	li s0, IOCONF_VAL_24
	sw s0, IOCONF_OFS(24)
#endif

#ifdef IOCONF_VAL_25
	li s0, IOCONF_VAL_25
	sw s0, IOCONF_OFS(25)
#endif

#ifdef IOCONF_VAL_26
	li s0, IOCONF_VAL_26
	sw s0, IOCONF_OFS(26)
#endif

#ifdef IOCONF_VAL_27
	li s0, IOCONF_VAL_27
	sw s0, IOCONF_OFS(27)
#endif

#ifdef IOCONF_VAL_28
	li s0, IOCONF_VAL_28
	sw s0, IOCONF_OFS(28)
#endif

#ifdef IOCONF_VAL_29
	li s0, IOCONF_VAL_29
	sw s0, IOCONF_OFS(29)
#endif

#ifdef IOCONF_VAL_30
	li s0, IOCONF_VAL_30
	sw s0, IOCONF_OFS(30)
#endif

#ifdef IOCONF_VAL_31
	li s0, IOCONF_VAL_31
	sw s0, IOCONF_OFS(31)
#endif

#ifdef IOCONF_VAL_32
	li s0, IOCONF_VAL_32
	sw s0, IOCONF_OFS(32)
#endif

#ifdef IOCONF_VAL_33
	li s0, IOCONF_VAL_33
	sw s0, IOCONF_OFS(33)
#endif

#ifdef IOCONF_VAL_34
	li s0, IOCONF_VAL_34
	sw s0, IOCONF_OFS(34)
#endif

#ifdef IOCONF_VAL_35
	li s0, IOCONF_VAL_35
	sw s0, IOCONF_OFS(35)
#endif

#ifdef IOCONF_VAL_36
	li s0, IOCONF_VAL_36
	sw s0, IOCONF_OFS(36)
#endif

#ifdef IOCONF_VAL_37
	li s0, IOCONF_VAL_37
	sw s0, IOCONF_OFS(37)
#endif

	// Trigger load
	li s0, 1
	sw s0, 0(a0)

1:
	nop
	lw s0, 0(a0)
	bne s0, zero, 1b

	// Infinite loop
1:
	nop
	j 1b
