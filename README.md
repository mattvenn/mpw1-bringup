# MPW1 bringup notes

See this [doc pack](https://docs.google.com/document/d/1lKKtgcVXwYAe81afha8X3PpY4TEB0o6XlIWKrYT2A7c/edit#) for:

* Overview of bringup process
* Blog post/videos
* Links to postmortem board
* MPW1 issues
* Physical package, pinning
* Scans/SEM
* Designs
* GDS

## rough voltage scan

    ./control.py --port /dev/ttyUSB1  vdd-scan

1st number is raw dac. eg (366 * 3.3 / 1024) = 1.18v.
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

* See ./vdd-scans for more scanning.
* Got chips 1, 2 & 10 working

## reliability

    ./control.py --port /dev/ttyUSB1  vdd-reliability --vdd-min 350 --vdd-max 380

1st number is DAC 2nd is % (0 to 1)

     352 0.000000
     353 0.010000
     354 1.000000
     355 1.000000
     356 1.000000

To load binary firmware:

    ./sw/control.py --vdd 355 --vdd1 450 --vdd2 450 simple_runner --firmware-bin ./fw/test-matt.bin
                          ^^^
                    This number is the core voltage, use something in the middle of the range of 100% reliability

## rescan

need to rescan all for coarse.
only got 1, 2 and 10 with any usable range

## firmware tweaking on 7seg

this gets 5 out of 7 segs

./sw/control.py --vdd 378 --vdd1 500 --vdd2 500 simple_runner --firmware-bin ./fw/test-matt-300-3.bin

## sense board

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

## VGA clock bringup

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

## Thu 17 Feb 12:30:18 CET 2022

changed pin 13 vsync config and pin 14 to match 7 seg and now don't need pullup
colour b1 is working

* 8  adj sec works
* 9  adj min works
* 10 adj hr  works
* 12 hsync   works
* 13 vsync   works
* 14 b1      either 14 or 15
* 15 b2
* 16 g1      works
* 17 g2      works
* 18 r1      works
* 19 r2      works

## Timing

As the bringup board is set to 50.25Mhz.
VGA board needs 31.5 to count in seconds.

Updating PLL and Serial settings in the bringup RTL:

-               .DIVF(7'b1000010), // 50.25
+               .DIVF(7'b1010011), // 63

and 
-               .UART_DIV(25), // 2 Mbaud
+               .UART_DIV(30), // 2 Mbaud

Then clkdiv 2 results in 31.5.
The build fails as it doesn't meet timing (only 61 MHz), but still seems to work.

Then the panel doesn't lock, but increasing the logic supply voltage vdd1 from 400 to 420 then works:

    ./sw/control.py --port /dev/ttyUSB1 --vdd 378 --vdd1 420 --vdd2 400 vga
    ./sw/control.py --port /dev/ttyUSB0 --vdd 378 --vdd1 425 --vdd2 400 vga

for future ref if icebreaker needs reflashing:

    cd pyfive-mpw1-postmortem/icebreaker/bringup/ #and check on matt-vga branch
    matt-desktop:2004 [matt-vga]: make prog
    cd -
    export CROSS=riscv64-unknown-elf-
    ./sw/control.py --port /dev/ttyUSB1 --vdd 375 --vdd1 425 --vdd2 400 vga




## WS2812 bringup


remove clk div stuff from control

add the extra load line 

	li a0, 0x00000000

otherwise switches back to sevenseg

worked straight away

waveform looks a bit slow to rise. ws2812 might have problems reading it.

but it works, hooked up to the dygma shortcut proto. animation lasts a few seconds before cpu hangs

    export CROSS=riscv64-unknown-elf-
    ./sw/control.py --port /dev/ttyUSB1 --vdd 370 --vdd1 400 --vdd2 400 ws2812 # for IC 1

# challenge TPM2137

* plug a wire from usr1 to io8
* logic analyser on 8, 9 & 10
* 10m clock

	// challenge proj_6 (.uart(proj6_io_in[8]), .clk_10(proj6_clk), .led_green(proj6_io_out[9]), .led_red(proj6_io_out[10]));
	// 8 input
	// 9 output
	// 10 output

control.py can control a uart on the fpga

    pass is q3kmvenn

9 and 10 outputs are both high all the time

    export CROSS=riscv64-unknown-elf-
    ./sw/control.py --port /dev/ttyUSB2 --vdd 378 --vdd1 400 --vdd2 400 challenge

needed to change config of IO to

	li s3, 0x0040 // was 80
	sw s3, IOCONF_OFS(9)

then all works!

# 7seg last segment

can disable pin 14 and enable 13,
or enable 13 and disable 14

tnt: so my guess is that the bit that end up in bit 0 of pin 14 config and bit 12 of pin 13 config are the same ... problem is the former is the bit that assigns the IO 14 to the management core and the latter is the one enabling the output driven of pin 13.

https://antmicro-skywater-pdk-docs.readthedocs.io/en/latest/contents/libraries/sky130_fd_io/docs/user_guide.html#io-drive-strength-modes

# Wed  4 May 10:18:15 CEST 2022

helping with James A, wants vdd scan. Only works with original frequency

    cd /home/matt/work/asic-workshop/shuttle1/bringup/pyfive-mpw1-postmortem/icebreaker/bringup
    git checkout main
    make prog

then for vga (with different pll)

    git checkout matt-vga
    make prog

# Thu 26 May 10:09:32 CEST 2022

got chip2 working with vga, just needed extra pins soldering and a new vdd
didn't boot till power cycled the fpga tho

    ./sw/control.py --port /dev/ttyUSB1 --vdd 424 --vdd1 420 --vdd2 400 vga
