 ./control.py --port /dev/ttyUSB1  vdd-scan

1st number is raw dac. eg (366 * 3.3 / 1024) = 1.18v
2nd number is number of chip select transitions, should be around 1000

 338 -1
 340 -1
 342 -1
 344 144
 346 1588
 348 1620
 350 1620
 352 1619
 354 923
 356 905
 358 905
 360 904
 362 904
 364 904
 366 904
 368 905
 370 905
 372 905
 374 905
 376 905
 378 905
 380 805
 382 -1
 384 -1
 386 -1
 388 58

 ./control.py --port /dev/ttyUSB1  vdd-reliability --vdd-min 350 --vdd-max 380

 1st number is DAC 2nd is % (0 to 1)

 352 0.000000
 353 0.010000
 354 1.000000
 355 1.000000
 356 1.000000

./sw/control.py --vdd 370 --vdd1 450 --vdd2 450 simple_runner --firmware-bin ./fw/test-matt.bin

# rescan

need to rescan all for coarse.
only got 1, 2 and 10 with any usable range

# firmware tweak

this gets 5 out of 7 segs

./sw/control.py --vdd 378 --vdd1 500 --vdd2 500 simple_runner --firmware-bin ./fw/test-matt-300-3.bin

# sense board

to get further, build a sense board as specced by tnt.
new control.py

export CROSS=riscv64-unknown-elf-


and the two pin female header plugs into the pins USR4/USR5 on the post-mortem board.
100k (red) into the USR4 and direct wire (brown) into USR5

as control.py will build fw

./sw/control.py --vdd 375 --vdd1 480 --vdd2 480 io-mapper --bit-start 195 --io-min 13  --io-max 13

can't ever find 12
tried with 370, 375, 367, 377, 378

to test just io12, move sense 0 to io 12 and run this:

    ./sw/control.py --vdd 373 --vdd1 480 --vdd2 480 io-mapper --bit-start 178 --io-min 12  --io-max 12

sweeping from 370 to 378

# vga bringup

	// Enable project 2
	li a0, 0x30000000
	li s0, 2
	sw s0, 0(a0)

did the scaning again, tnt generated the list of config bits to setup the outputs correct (ignore inputs). This worked after getting logic analyser connected to correct pins.

    time.sleep(1)
    self.ctrl.set_clk_div(2)

didn't work but

    time.sleep(1)
    self.ctrl.set_clk_div(4)
    time.sleep(1)
    self.ctrl.set_clk_div(2)

did work. pin 12 is slow to rise as bad config. but with a 220R pullup get vga sync on the small monitor

seems 1 colour is not working

# Inputs not working

Need to program the mux to set the oeb correct

    // set the oeb reg to get inputs working
	li s0, (1 << 8) + (1 << 9) + (1 << 10)
	sw s0, 4(a0)

but this doesn't help with being able to adjust the time

# ws2812 bringup

remove clk div stuff from control

add the extra load line 

	li a0, 0x00000000

otherwise switches back to sevenseg

worked straight away

waveform looks a bit slow to rise. ws2812 might have problems reading it.
