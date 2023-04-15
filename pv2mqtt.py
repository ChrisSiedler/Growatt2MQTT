#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
import logging.handlers as Handlers
import argparse
from threading import Thread, Lock


parser = argparse.ArgumentParser()
loggroup = parser.add_mutually_exclusive_group(required=False)
loggroup.add_argument("-q", "--quiet",   action="store_const", dest="loglevel", const=logging.ERROR, help="only error output", default=logging.WARNING)
loggroup.add_argument("-v", "--verbose", action="store_const", dest="loglevel", const=logging.INFO,  help="increase output verbosity")
loggroup.add_argument("-d", "--debug",   action="store_const", dest="loglevel", const=logging.DEBUG, help="debug output")

args = parser.parse_args()

# =========================================================================================
# =========================================================================================

log = logging.getLogger()
log.setLevel(logging.DEBUG)

ConsoleLogHandler = logging.StreamHandler()
ConsoleLogHandler.setLevel(args.loglevel)
ConsoleLogHandler.setFormatter(logging.Formatter('%(levelname)s:	%(message)s'))

log.addHandler(ConsoleLogHandler)

# =========================================================================================
# =========================================================================================

import math
import datetime
import json
import paho.mqtt.client as mqtt
import pprint
pp = pprint.PrettyPrinter(indent=4)

MQTT_Settings = {
	"Server":		"10.10.98.71",
	"Port":     	1883,
	"AMS_Topic":	"powermeter",
	"PV_Topic":		"pv2",
	"keepalive":	60
	}
	
mqttpvtopic = MQTT_Settings['PV_Topic']

RS485PortInv = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0' # Inverter

#------------------
threads = {}
mqttlock = Lock()

import growatt
import ModBusDev as MBD

#============================================================================


def mqtt_listen():
	global mq1

	def mqtt_on_connect(client, userdata, flags, rc):
		# This will be called once the client connects
		logging.info(f"MQTT connected with result code {rc}")

		# Subscribe here!
		client.subscribe(f"{mqttpvtopic}/Active_P_Rate/set")
		client.subscribe(f"{mqttpvtopic}/read_raw/get")

	# ------------------------------------------------------------------------------
	def mqtt_event(client, userdata, msg):
		logging.debug(f"Message received [{msg.topic}]: {msg.payload}")

		try:
		
			if msg.topic == f"{mqttpvtopic}/Active_P_Rate/set":
				val = int(msg.payload.decode("utf-8"))
				logging.info(f"setting Active_P_Rate to {val}%")
				gw1.write("Active_P_Rate", val)
				
			# --------------------------
			elif msg.topic == f"{mqttpvtopic}/read_raw/get":

				d = json.loads(msg.payload.decode("utf-8"))
				ans = {"q":d}

				rtype = getattr(MBD.registerType, d['rtype'])
				dtype = getattr(MBD.registerDataType, d['dtype'])
				vtype = int if d['vtype'] == "int" else str

				x = d['addr'],d['count'],rtype, dtype, vtype,"read_raw","",1,1
				ans['ans'] = gw1._read(x)

				logging.info(ans)
				with mqttlock:
					client.publish(f"{mqttpvtopic}/read_raw", json.dumps(ans))
				client.loop()

			# --------------------------
			else:
				logging.warning("Don't know what to do with that...")			
		
		except Exception as e:
			logging.error(f"{e}")	
			


	mq1 = mqtt.Client()

	mq1.will_set(f"{mqttpvtopic}/status", "Offline", qos=1, retain=False)
	mq1.on_connect = mqtt_on_connect
	mq1.on_message = mqtt_event
	mq1.connect(MQTT_Settings['Server'], MQTT_Settings['Port'], 60)

	mq1.loop_forever()  # Start networking daemon

# =====================================================================================
# =====================================================================================


def mean(dataset):
    return sum(dataset) / len(dataset)


def sm_reader_work():
	global mq1

	list0  = ["Status", "PV_P", "AC_P"]

	list1  = ["On_Off", "Status", "PV_P", "PV1_U", "PV1_I", "PV1_P", "PV2_U", "PV2_I", "PV2_P", "AC_P", "AC_F", "AC1_I", "AC2_I", "AC3_I", "Energy_total", "PV1_E_total", "PV2_E_total", "Temp", 
	"DeratingMode", "FaultCode", "FaultBitcode", "FaultBitcode2", "WarningBit","Sys-Date", "Sys-Time"]

	list1 += ['Priority', 'Bat_P_discharge', 'Bat_P_charge', 'Bat_V', 'Bat_SOC', 'P_AC_2_User', 'P_AC_2_Grid', 'P_Inv_2_local', 'Bat_E_discharge', 'Bat_E_charge', 'EPS1_U', 'EPS1_I', 'EPS1_P', 'EPS2_U', 'EPS2_I', 'EPS2_P', 'EPS3_U', 'EPS3_I', 'EPS3_P', 'EPS_load', 'Active_P_Rate', 'SerialNo', 'FW-Build', 'BAT_CC', 'BAT_LV', 'BAT_CV', 'LoadFirst_StopSOC', 'GridFirst_DischargeRate', 'GridFirst_StopSOC', 'BattFirst_StopSOC']


	gw1 = growatt.SPH(
		device=RS485PortInv,
		stopbits=1,
		parity="N",
		baud=9600,
		timeout=1,
		unit=1
		)


	logging.info('Modbus Inverter connected')

	sleep1 = 0.2
	lastrun = datetime.datetime.now()

	while True:
		
#		try:

			# only short round:
			if (datetime.datetime.now() - lastrun).seconds < 5:
				info = gw1.read_list(list0)
#				print(info)

				if info == {}: 
					logging.warning(f"No data from inverter received")
					time.sleep(sleep1)
					continue

			else:

				lastrun = datetime.datetime.now()

				info  = gw1.read_list(list1)
				
				if info == {}: # no info:
					logging.warning(f"No data from inverter received")
					with mqttlock:
						mq1.publish(f"{mqttpvtopic}/status", "Offline")

					time.sleep(sleep1)
					continue

				# error:
				if not 'Status' in info: 
					with mqttlock:
						mq1.publish(f"{mqttpvtopic}/status", "Script error")

					logging.error(f"Error: no status in data, data: {info}")
					time.sleep(60)
					continue

				for k,v in info.items():
					if isinstance(v, float):
						info[k] = round(v,3)

				logging.debug(pp.pformat(info))

				with mqttlock:
					mq1.publish(f"{mqttpvtopic}/status", info.pop('Status'))
					mq1.publish(f"{mqttpvtopic}/data", json.dumps(info))

				logging.info(f"PV 2 MQTT update send {lastrun}")
			
			time.sleep(sleep1)

#		except Exception as e: 
#			logging.error(f"Error: {e}")
#			pass


threads['sm_reader'] = Thread(target=sm_reader_work)
threads['sm_reader'].start()

mqtt_listen()

while True:
	time.sleep(1)

#mq1.disconnect()
logging.info('shutting down')

