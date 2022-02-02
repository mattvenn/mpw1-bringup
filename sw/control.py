#!/usr/bin/env python3

#
# Copyright (C) 2020-2022  Sylvain Munaut <tnt@246tNt.com>
# SPDX-License-Identifier: MIT
#

import argparse
import binascii
import os
import random
import serial
import subprocess
import struct
import sys
import tempfile
import time
import yaml


# ----------------------------------------------------------------------------
# Serial commands
# ----------------------------------------------------------------------------

class WishboneInterface(object):

	COMMANDS = {
		'SYNC' : 0,
		'REG_ACCESS' : 1,
		'DATA_SET' : 2,
		'DATA_GET' : 3,
		'AUX_CSR' : 4,
	}

	def __init__(self, port):
		self.ser = ser = serial.Serial()
		ser.port = port
		ser.baudrate = 2000000
		ser.stopbits = 2
		ser.timeout = 0.1
		ser.open()

		if not self.sync():
			raise RuntimeError("Unable to sync")

	def sync(self):
		for i in range(10):
			self.ser.write(b'\x00')
			d = self.ser.read(4)
			if (len(d) == 4) and (d == b'\xca\xfe\xba\xbe'):
				return True
		return False

	def write(self, addr, data):
		cmd_a = ((self.COMMANDS['DATA_SET']   << 36) | data).to_bytes(5, 'big')
		cmd_b = ((self.COMMANDS['REG_ACCESS'] << 36) | addr).to_bytes(5, 'big')
		self.ser.write(cmd_a + cmd_b)

	def read(self, addr):
		cmd_a = ((self.COMMANDS['REG_ACCESS'] << 36) | (1<<20) | addr).to_bytes(5, 'big')
		cmd_b = ((self.COMMANDS['DATA_GET']   << 36)).to_bytes(5, 'big')
		self.ser.write(cmd_a + cmd_b)
		d = self.ser.read(4)
		if len(d) != 4:
			raise RuntimeError('Comm error')
		return int.from_bytes(d, 'big')

	def aux_csr(self, value):
		cmd = ((self.COMMANDS['AUX_CSR'] << 36) | value).to_bytes(5, 'big')
		self.ser.write(cmd)


class DummyWishboneInterface(object):

	def write(self, addr, data):
		print(f"W {addr:05x} {data:08x}")

	def read(self, addr):
		print(f"R {addr:05x}")
		return 0

	def aux_csr(self, value):
		print(f"A {value:08x}")


# ----------------------------------------------------------------------------
# Controller
# ----------------------------------------------------------------------------

class Controller:

	def __init__(self, wb):
		# Save IF
		self.wb = wb

		# Default config
		self.clk_div    = 2 # Div-by-8
		self.rst_mode   = 0 # Asserted
		self.rst_period = 3
		self.rst_length = 2

		# Sync
		self._update_crg()

	def _update_crg(self):
		self.wb.write(0x00000,
			(self.rst_period << 6) |
			(self.rst_length << 4) |
			(self.rst_mode   << 2) |
			(self.clk_div    << 0)
		)

	def set_clk_div(self, div):
		DIV = { 2: 0, 4: 1, 8: 2, 16: 3 }
		self.clk_div = DIV[div]
		self._update_crg()

	def set_reset(self, rst):
		self.rst_mode = 0 if rst else 1
		self._update_crg()

	def set_reset_auto(self):
		self.rst_mode = 2
		self._update_crg()

	def set_voltages(self, vdd, vdd1, vdd2):
		self.wb.write(0x00001, (vdd << 20) | (vdd1 << 10) | (vdd2 << 0))

	def load_fw(self, filename):
		with open(filename, 'rb') as fh:
			addr = 0
			active = True
			while True:
				b = fh.read(4)

				if len(b) == 0:
					break;
				elif len(b) < 4:
					b = (b + b'\x00\x00\x00')[0:4]

				self.wb.write(0x10000 + addr, struct.unpack('<I', b)[0])
				addr += 1

	def query_spi_cmd_count(self):
		return self.wb.read(0x10000)

	def iom_drive(self, val, strong):
		if val is None:
			self.wb.write(0x30000, 0)
		else:
			self.wb.write(0x30000,
				(0x3 if val else 0x00) |
				(0x8 if strong else 0x4)
			)

	def iom_sense(self):
		# Reset value
		self.wb.write(0x30008, 0)

		# Wait a bit for sensing
		time.sleep(0.1)

		# Read all registers
		rv = []

		for i in range(8):
			x = self.wb.read(0x30008 + i)
			rv.append( ((x & 0xffff), (x >> 16)) )

		return rv


# ----------------------------------------------------------------------------
# Test sequences
# ----------------------------------------------------------------------------

class BaseTest:

	# Keys from config (required, default)
	CFG_KEYS = {
		'vdd':	(True, None),
		'vdd1':	(True, None),
		'vdd2':	(True, None),
	}

	def __init__(self, ctrl, args):
		# Save params
		self.ctrl = ctrl
		self.args = args

		# Build config
		self._load_config()

	def _load_config(self):

		# Default config
		self.cfg = dict([(k, d) for k, (r,d) in self.CFG_KEYS.items()])

		# Config file
		if self.args.config:
			# Load file
			cfg_file = yaml.load(self.args.config, yaml.CLoader)

			# Load defaults
			self.cfg.update(cfg_file.get('defaults', {}))

			# Test specific values
			self.cfg.update(cfg_file.get(self.name, {}))

			# Die specific
			if self.args.die and (self.args.die in cfg_file.get('dies', {})):
				die_cfg = cfg_file['dies'][self.args.die]
				self.cfg.update(die_cfg.get('defaults', {}))
				self.cfg.update(die_cfg.get(self.name, {}))

		# Argument overrides
		for k in self.CFG_KEYS:
			if getattr(self.args, k) is not None:
				self.cfg[k] = getattr(self.args, k)

		# Check required
		for k, (r,d) in self.CFG_KEYS.items():
			if self.cfg[k] is None:
				raise ValueError(f"Required config value missing for '{k}'")

	def _get_fw_path(self, file=None):
		elems = [ os.path.dirname(__file__), '../fw' ] + ([file] if file is not None else [])
		return os.path.abspath(os.path.join(*elems))

	def load_fw(self, filename=None):
		self.ctrl.load_fw(self._get_fw_path(filename or f'test-{self.name}.bin'))

	def build_and_load_fw(self, filename, defs={}):
		# Env
		CROSS  = os.getenv('CROSS', 'riscv-none-embed-')
		CFLAGS = os.getenv('CFLAGS', '-march=rv32i -mabi=ilp32 -ffreestanding -nostartfiles --specs=nano.specs -I.')

		# Build the defines
		opt_defs = [f'-D{k}={v}' for k,v in defs.items()]

		# Build in temp dir
		with tempfile.TemporaryDirectory() as tmpdir:
			subprocess.call([
				CROSS + 'gcc',
				*CFLAGS.split(),
				*opt_defs,
				'-o', os.path.join(tmpdir, 'fw.elf'),
				self._get_fw_path(filename)
			])
			subprocess.call([
				CROSS + 'objcopy',
				'-O', 'binary',
				os.path.join(tmpdir, 'fw.elf'),
				os.path.join(tmpdir, 'fw.bin')
			])
			self.ctrl.load_fw(os.path.join(tmpdir, 'fw.bin'))

	@classmethod
	def _all_subclasses(cls):
		return set(cls.__subclasses__()).union(
			[s for c in cls.__subclasses__() for s in c._all_subclasses()]
		)

	@classmethod
	def get_all_tests(kls):
		return dict([(cls.name, cls) for cls in BaseTest._all_subclasses()])

	@classmethod
	def get_test_by_name(kls, test_name):
		return kls.get_all_tests().get(test_name)

	@classmethod
	def get_test_for_args(kls, args):
		return kls.get_all_tests().get(args.test_name)

	@classmethod
	def setup_arg_parser(self, parser):
		# Common option
		parser.add_argument('--vdd', type=int,
			help="Set VDD  level (0-1023)")
		parser.add_argument('--vdd1', type=int,
			help="Set VDD1 level (0-1023)")
		parser.add_argument('--vdd2', type=int,
			help="Set VDD2 level (0-1023)")

		parser.add_argument('--config', type=argparse.FileType('r'), metavar="FILE",
			help="Config file to load per-die values")
		parser.add_argument('--die', type=int, metavar="N",
			help="Die number to select")

		# Per-test option
		subparsers = parser.add_subparsers(dest='test_name', required=True)

		for name, cls in sorted(self.get_all_tests().items()):
			if callable(getattr(cls, '_setup_custom_args')):
				sp = subparsers.add_parser(name, help=f'{name} help')
				cls._setup_custom_args(sp)


class SimpleRunnerTest(BaseTest):

	name = 'simple_runner'

	@classmethod
	def _setup_custom_args(kls, parser):
		fw_grp = parser.add_mutually_exclusive_group()
		fw_grp.add_argument("--firmware-bin", type=str, metavar="BIN",
			help="Firmare binary to load")
		fw_grp.add_argument("--firmware-src", type=str, metavar="SRC",
			help="Firmare source to build and load")
		parser.add_argument("--reset-loop", action='store_true', default=False,
			help="Enable auto-reset loop once loaded")

	def run(self):
		self.ctrl.set_reset(True)
		self.ctrl.set_voltages(self.cfg['vdd'], self.cfg['vdd1'], self.cfg['vdd2'])
		self.ctrl.load_fw(self.args.firmware_bin)
		self.ctrl.set_reset(False)
		time.sleep(1)
		self.ctrl.set_clk_div(4)
#		time.sleep(1)
#		self.ctrl.set_clk_div(2)


class VDDScanTest(BaseTest):

	name = 'vdd-scan'

	CFG_KEYS = {}

	@classmethod
	def _setup_custom_args(kls, parser):
		parser.add_argument("--vdd-min", type=int, metavar="MIN", default=300,
			help="Minimum VDD value to try")
		parser.add_argument("--vdd-max", type=int, metavar="MAX", default=600,
			help="Maximum VDD value to try")
		parser.add_argument("--vdd-step", type=int, metavar="STEP", default=2,
			help="Maximum VDD value to try")
		parser.add_argument("--retry", type=int, metavar="N", default=3,
			help="Number of retries")
		parser.add_argument("--cmd-min", type=int, metavar="MIN", default=50,
			help="Minimum number of SPI commands to be considered valid")
		parser.add_argument("--cmd-max", type=int, metavar="MAX", default=None,
			help="Maximum number of SPI commands to be considered valid")
		parser.add_argument("--cmd-no-limit", action="store_true", default=False,
			help="Print all results, don't filter on potential validity")

	def run(self):
		# Assert reset
		self.ctrl.set_reset(True)

		# Load firmware
		self.ctrl.load_fw(self._get_fw_path("test-vdd-scan.bin"))

		# Scan
		for vdd in range(self.args.vdd_min, self.args.vdd_max+1, self.args.vdd_step):
			# Set all voltages
			self.ctrl.set_voltages(vdd, vdd, vdd)

			# Retry if needed
			for i in range(self.args.retry):
				# Set reset to manual, assert and release
				self.ctrl.set_reset(True)
				self.ctrl.set_reset(False)

				# Wait a bit and print command count
				time.sleep(.1)

				cc = self.ctrl.query_spi_cmd_count()

				# Filter
				if self.args.cmd_no_limit or (
						((self.args.cmd_min is None) or (self.args.cmd_min < cc)) and
						((self.args.cmd_max is None) or (self.args.cmd_max > cc))
					):
					# Print
					print(f"{vdd:d} {cc:d}")
					break

			else:
				print(f"{vdd:d} -1")


class VDDReliabilityTest(BaseTest):

	name = 'vdd-reliability'

	CFG_KEYS = {}

	@classmethod
	def _setup_custom_args(kls, parser):
		parser.add_argument("--vdd-min", type=int, metavar="MIN", required=True,
			help="Minimum VDD value to try")
		parser.add_argument("--vdd-max", type=int, metavar="MAX", required=True,
			help="Maximum VDD value to try")
		parser.add_argument("--vdd-step", type=int, metavar="STEP", default=1,
			help="Maximum VDD value to try")
		parser.add_argument("--samples", type=int, metavar="N", default=100,
			help="Number of samples")
		parser.add_argument("--cmd-min", type=int, metavar="MIN", default=900,
			help="Minimum number of SPI commands to be considered valid")
		parser.add_argument("--cmd-max", type=int, metavar="MAX", default=1100,
			help="Maximum number of SPI commands to be considered valid")

	def run(self):
		# Assert reset
		self.ctrl.set_reset(True)

		# Load firmware
		self.ctrl.load_fw(self._get_fw_path("test-vdd-scan.bin"))

		# Scan
		for vdd in range(self.args.vdd_min, self.args.vdd_max+1, self.args.vdd_step):
			# Set all voltages
			self.ctrl.set_voltages(vdd, vdd, vdd)

			# Test multiple times
			ok = 0

			for i in range(self.args.samples):
				# Set reset to manual, assert and release
				self.ctrl.set_reset(True)
				self.ctrl.set_reset(False)

				# Wait a bit and print command count
				time.sleep(.1)

				cc = self.ctrl.query_spi_cmd_count()

				# Filter
				if self.args.cmd_min < cc < self.args.cmd_max:
					ok += 1

			print(f"{vdd:d} {ok/self.args.samples:f}")


class IOMapperTest(BaseTest):

	name = 'io-mapper'

	@classmethod
	def _setup_custom_args(kls, parser):
		parser.add_argument("--io-min", type=int, metavar="MIN", default=11,
			help="Minimum IO to map")
		parser.add_argument("--io-max", type=int, metavar="MAX", default=27,
			help="Maximum IO to map")
		parser.add_argument("--bit-start", type=int, metavar="N",
			help="Bit number to start the scan from")
		parser.add_argument("--bit-window", type=int, metavar="N", default=2,
			help="Max bit number deviation compared to expected value")

	def _build_io_config(self, bits):
		# Empty vector
		v = [0 for i in range(38*13)]

		# Set bits
		for b in bits:
			v[b] = 1

		# Build each io config
		rv = {}

		for i in range(38):
			ioc = sum([(bv << bn) for bn, bv in enumerate(v[13*i:13*(i+1)])])
			if ioc:
				rv[f'IOCONF_VAL_{i}'] = f'0x{ioc:04x}'

		return rv

	def _bitval(self, sv):
		if sv == (0, 65535):
			return '1'
		elif sv == (65535, 0):
			return '0'
		else:
			return 't'

	def run(self):
		# Config
		ATTEMPTS = [
		#	( "UM",   [0, -1], None ),		# User mode driver
			( "MM",   [0, -1, -12], '0' ),	# Mgmt drive low
			( "MM-1", [0, -1, -13], '0' ),	# Mgmt drive low (internal shift = -1)
			( "MM+1", [0, -1, -11], '0' ),	# Mgmt drive low (internal shift = +1)
		]

		# Loop init
		bn_cur = self.args.bit_start or ((self.args.io_min * 13) + 12)
		wiring = {}
		first = True

		# Scan all the IO we're trying to find
		for io_num in range(self.args.io_min, self.args.io_max+1):
			# If we need wiring, ask the user to wire things up
			if io_num not in wiring:
				# Reset
				wiring = {}

				# Probe the user
				print("[+] Rewire probing harness as follows :")

				# Assign in order
				for i,j in enumerate(range(io_num, min(io_num+8, self.args.io_max+1))):
					wiring[j] = i
					print(f"    - Sense wire {i:d} to IO {j:2d}")

				# Wait for user
				input()

			# Debug
			print(f"[+] Probing for IO {io_num} starting at bit {bn_cur}")

			# Boundaries of what bits to try
			if first:
				bn_min = bn_cur
				bn_max = 13 * 38
			else:
				bn_min = bn_cur
				bn_max = bn_cur + 2 * self.args.bit_window + 1

			first = False

			# Try those bits
			for bn in range(bn_min, bn_max):
				# Debug
				print(f"[.]  Bit {bn:d}")

				# Attempts
				for name, bo, exp in ATTEMPTS:
					# IO config to try
					defs = self._build_io_config([x + bn for x in bo])

					# Configure the board
					self.ctrl.set_reset(True)
					self.ctrl.set_voltages(self.cfg['vdd'], self.cfg['vdd1'], self.cfg['vdd2'])
					self.build_and_load_fw("test-io-mapper.S", defs=defs)
					self.ctrl.set_reset(False)

					# Try to drive the pin
					self.ctrl.iom_drive(0, True)
					ss0 = self.ctrl.iom_sense()[wiring[io_num]]

					self.ctrl.iom_drive(1, True)
					ss1 = self.ctrl.iom_sense()[wiring[io_num]]

					self.ctrl.iom_drive(None, False)

					# Is it actively driven ?
					if self._bitval(ss0) == self._bitval(ss1):
						# Yes !
						print(f"Found {bn} {name}")
						bn_cur = bn + 13 - self.args.bit_window
						break

						# Done for this

				else:
					# Try next bit
					continue

				# We found something
				break

			else:
				# Nothing found, try to skip over it
				bn_cur = bn_cur + 13


class IOMapperDebugTest(IOMapperTest):

	name = 'io-mapper-debug'

	def run(self):
		bn = 183
		bo = [0,-1, -12]
		name = 'X'
		wiring = { 12: 1 }
		io_num = 12

		bn = 196
		wiring = { 12: 2 }

		TESTS = []
		for top in range(8):
			for bot in range(16):
				v = []

				if top & 1:
					v.append(1)
				if top & 2:
					v.append(0)
				if top & 4:
					v.append(-1)

				if bot & 1:
					v.append(-11)
				if bot & 2:
					v.append(-12)
				if bot & 4:
					v.append(-13)
				if bot & 8:
					v.append(-14)

				TESTS.append(v)

		print(TESTS)
		print(len(TESTS))

		for bn in range(bn-3, bn+4):
			for bo in TESTS:

				defs = self._build_io_config([x + bn for x in bo])
				print(defs)

				# Configure the board
				self.ctrl.set_reset(True)
				self.ctrl.set_voltages(self.cfg['vdd'], self.cfg['vdd1'], self.cfg['vdd2'])
				self.build_and_load_fw("test-io-mapper.S", defs=defs)
				self.ctrl.set_reset(False)

				# Try to drive the pin
				self.ctrl.iom_drive(0, False)
				ss0 = self.ctrl.iom_sense()[wiring[io_num]]

				self.ctrl.iom_drive(1, False)
				ss1 = self.ctrl.iom_sense()[wiring[io_num]]

				if self._bitval(ss0) == self._bitval(ss1):
					print(f"Found {bn} {name}")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
	# Argument parsing
	parser = argparse.ArgumentParser()

	parser.add_argument('--port', type=str, default='/dev/ttyUSB1', help='USB port to use for device comms')
	BaseTest.setup_arg_parser(parser)

	args = parser.parse_args()

	# Connect to board
	wb = WishboneInterface(args.port)
	#wb = DummyWishboneInterface()
	ctrl = Controller(wb)

	# Create and run test
	test_cls = BaseTest.get_test_for_args(args)
	test = test_cls(ctrl, args)
	test.run()

	# Done
	return 0


if __name__ == '__main__':
	sys.exit(main() or 0)
