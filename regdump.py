#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import logging

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

root = logging.getLogger()
root.setLevel(logging.WARNING)
root.addHandler(handler)

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.payload import BinaryPayloadBuilder


RS485Port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0'


class Inverter:
	def __init__(self, RS485Port):
		self.client = ModbusClient(method='rtu', port=RS485Port, baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
		self.client.connect()
		logging.info('Modbus connected')

	def read(self, start, length=1, regtype="holding"):
		return self.client.read_holding_registers(start, length).registers

	def close(self):
		self.client.close()



Inv1 = Inverter(RS485Port)
reglimit = 100
displ = 20


def disphex(d, start=0):
	i=0
	print("\n      "+' '.join([f"{i:5}" for i in range(displ)]))

	while i < len(d):
		reg = start+i
		di = d[i:i+displ]
		#di = ' '.join([f"{v:04x}" for v in di])
		di = ' '.join([f"{v:5}" for v in di])
		print(f"{reg:04}: {di}")
		i+=displ



def regdump(start, length):
	pos = start
	end = start + length
	d =[]
	while pos < end:
		readl = min(reglimit, (end - pos))
#		print(f"reading: {pos} {readl}")
		d += Inv1.read(pos, readl, "holding")
		pos += readl
		
	disphex(d, start)
	
	
# =====================================================

regdump(   0,125)
regdump(1000,125)

#regdump(3000,125)

Inv1.close()


