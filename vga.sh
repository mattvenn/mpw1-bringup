export CROSS=riscv64-unknown-elf-
port=/dev/serial/by-id/usb-FTDI_Dual_RS232-HS-if01-port0
# was broken - fixed by changing --vdd from 375 to 370 on Wed 17 May 17:21:08 CEST 2023
./sw/control.py --port $port --vdd 370 --vdd1 440 --vdd2 375 vga
