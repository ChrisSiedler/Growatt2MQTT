#!/usr/bin/env python3

import sys
import growatt
import ModBusDev as MBD


RS485Port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0' # Inverter

inv1 = growatt.SPH(
    device=RS485Port,
    stopbits=1,
    parity="N",
    baud=9600,
    timeout=1,
    unit=1
)



print(f"{inv1}:")



print("\nInput Registers:")

for k, v in inv1.read_all(MBD.registerType.INPUT).items():
	address, length, rtype, dtype, vtype, label, fmt, sf = inv1.registers[k]

	if type(fmt) is list or type(fmt) is dict:
		print(f"\t{label: <40}: {v}")
	elif vtype is float:
		print(f"\t{label: <40}: {v:.2f}{fmt}")
	else:
		print(f"\t{label: <40}: {v}{fmt}")

print("\nHolding Registers:")

for k, v in inv1.read_all(MBD.registerType.HOLDING).items():
	if not k in inv1.registers:
		print(k,v)
		continue

	address, length, rtype, dtype, vtype, label, fmt, sf = inv1.registers[k]
#
	if type(fmt) is list:
		print(f"\t{label: <40}: {v}")
	elif type(fmt) is dict:
		print(f"\t{label: <40}: {fmt[str(v)]}")
	elif vtype is float:
		print(f"\t{label: <40}: {v:.2f}{fmt}")
	else:
		print(f"\t{label: <40}: {v}{fmt}")
