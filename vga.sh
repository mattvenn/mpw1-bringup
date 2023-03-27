export CROSS=riscv64-unknown-elf-
port=/dev/serial/by-id/usb-FTDI_Dual_RS232-HS-if01-port0
./sw/control.py --port $port --vdd 375 --vdd1 440 --vdd2 375 vga
