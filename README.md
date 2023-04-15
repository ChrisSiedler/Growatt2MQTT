# Growatt2MQTT

This is a python library to communicate with a Growatt SPH Inverter using RS485 / Modbus.

## Dependency:
 - pymodbus 2.5.3 -- not working with version 3.0
 
 
## Content:
`regdump.py` Dump the holding registers in HEX.  
Useful to store the current configuration, find and compare changes.

`growatt.py` This file contains the Growatt SPH specific modbus registers. Is used by the the following tools.

`ModBusDev.py` A library to communicate on Modbus in an "python way", this class does all the nneded transfromations of the data and looks up the needed registers. Is used by the the following tools.


`reader.py` Reads all configured registers and converts the output into human readable form.



## Background:


## Current status:
It's working.  
I use this code on an RaspberryPi 3 with debian 11 and an cheap USB-RS485 adapter with an CH340 controller.


