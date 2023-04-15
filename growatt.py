#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ModBusDev as MBD
from pymodbus.constants import Endian
import datetime

from pymodbus.payload import BinaryPayloadDecoder

rt = MBD.registerType
dt = MBD.registerDataType

def decode_status(i):
	reg = ["Standby","NoUse", "Discharge", "Fault", "Flash", "PVcharge", "ACcharge", "Combinecharge", "CombinechargeandBypass", "PVchargeandBypass", "ACchargeandBypass", "Bypass", "PVchargeandDischarge"]
	try:
		return reg[i]
	except IndexError:
		return "Unknown"
		
def decode_pf(i):
	reg = ["PF=1","PF by setting", "default PF line", "User PF line", "UnderExcited (Inda)", "OverExcited (Capa)", "Q(v) Model", "Direct Control mode"]
	try:
		return reg[i]
	except IndexError:
		return "Unknown"

class SPH(MBD.ModBusDev):

	def __init__(self, *args, **kwargs):
		self.model = "SPH"
		self.baud = 9600


		self.wordorder = Endian.Big
		self.byteorder = Endian.Big

		super().__init__(*args, **kwargs)

		self.registers = {
			"Status":  				(  0, 1, rt.INPUT, dt.UINT16, decode_status, "Inverter Status", "", 1),
			"PV_P":  				(  1, 2, rt.INPUT, dt.UINT32, float, "PV Power", "W", 0.1),
			"PV1_U":  				(  3, 1, rt.INPUT, dt.UINT16, float, "PV1 Voltage", "V", 0.1),
			"PV1_I":  				(  4, 1, rt.INPUT, dt.UINT16, float, "PV1 Current", "A", 0.1),
			"PV1_P":  				(  5, 2, rt.INPUT, dt.UINT32, float, "PV1 Power", "W", 0.1),

			"PV2_U":  				(  7, 1, rt.INPUT, dt.UINT16, float, "PV2 Voltage", "V", 0.1),
			"PV2_I":  				(  8, 1, rt.INPUT, dt.UINT16, float, "PV2 Current", "A", 0.1),
			"PV2_P":  				(  9, 2, rt.INPUT, dt.UINT32, float, "PV2 Power", "W", 0.1),

		
			"AC_P":  				( 35, 2, rt.INPUT, dt.UINT32, float, "Output power", "W", 0.1),
			"AC_F":  				( 37, 1, rt.INPUT, dt.UINT16, float, "Grid frequency", "Hz", 0.01),
			
			"AC1_U":  				( 38, 1, rt.INPUT, dt.UINT16, float, "AC R-S Voltage", "V", 0.1),
			"AC1_I":  				( 39, 1, rt.INPUT, dt.UINT16, float, "AC R-S Current", "A", 0.1),
			"AC1_P":  				( 40, 2, rt.INPUT, dt.UINT32, float, "AC R-S Power", "W", 0.1),		# siehe AC_P

			"AC2_U":  				( 42, 1, rt.INPUT, dt.UINT16, float, "AC S-T Voltage", "V", 0.1),
			"AC2_I":  				( 43, 1, rt.INPUT, dt.UINT16, float, "AC S-T Current", "A", 0.1),
			"AC2_P":  				( 44, 2, rt.INPUT, dt.UINT32, float, "AC S-T Power", "W", 0.1),		# immer 0

			"AC3_U":  				( 46, 1, rt.INPUT, dt.UINT16, float, "AC T-R Voltage", "V", 0.1),
			"AC3_I":  				( 47, 1, rt.INPUT, dt.UINT16, float, "AC T-R Current", "A", 0.1),
			"AC3_P":  				( 48, 2, rt.INPUT, dt.UINT32, float, "AC T-R Power", "W", 0.1),		# immer 0

			"Energy_total":  		( 55, 2, rt.INPUT, dt.UINT32, float, "Total generated energy", "kWh", 0.1),

			"PV1_E_total":  		( 61, 2, rt.INPUT, dt.UINT32, float, "PV1 Energy total", "kWh", 0.1),
			"PV2_E_total":  		( 65, 2, rt.INPUT, dt.UINT32, float, "PV2 Energy total", "kWh", 0.1),

			"Temp":  				( 93, 1, rt.INPUT, dt.UINT16, int, "Inverter temperature", "°C", 0.1),

#			"PBusV":  				( 98, 1, rt.INPUT, dt.UINT16, float, "P Bus inside Voltage", "V", 0.1),

#			"IPF":  				(100, 1, rt.INPUT, dt.UINT16, int, "Inverter output PF now", "", 1),
			"DeratingMode":  		(104, 1, rt.INPUT, dt.UINT16, int, "Derating Mode", "", 1),
			"FaultCode":  			(105, 1, rt.INPUT, dt.HEX, list, "Fault Code", "", 1),
			"FaultBitcode":  		(106, 2, rt.INPUT, dt.HEX, list, "Fault Bitcode", "", 1),
			"FaultBitcode2":  		(108, 2, rt.INPUT, dt.HEX, list, "Fault Bitcode2", "", 1),
			"WarningBit":  			(110, 2, rt.INPUT, dt.HEX, list, "Warning bit", "", 1),

#			"PriorityR":  			(118, 1, rt.INPUT, dt.UINT16, int, "Priority", ["Load", "Bat","Grid"], 1),
			"BAT_Type":  			(119, 1, rt.INPUT, dt.UINT16, int, "Battery Type", ["Lead-acid","Lithium","other"], 1),


			#----
			"Bat_P_discharge":  	(1009, 2, rt.INPUT, dt.UINT32, int, "Battery discharge Power", "W", 0.1),
			"Bat_P_charge":  		(1011, 2, rt.INPUT, dt.UINT32, int, "Battery charge Power", "W", 0.1),

			"Bat_V":  				(1013, 1, rt.INPUT, dt.UINT16, int, "Battery Voltage", "V", 0.1),
			"Bat_SOC":  			(1014, 1, rt.INPUT, dt.UINT16, int, "Battery SOC",     "%", 1),


			"P_AC_2_User":			(1021, 2, rt.INPUT, dt.UINT32, float, "AC power to User", "W", 0.1),
			"P_AC_2_Grid":			(1029, 2, rt.INPUT, dt.UINT32, float, "AC power to Grid", "W", 0.1),
			"P_Inv_2_local":		(1037, 2, rt.INPUT, dt.UINT32, float, "INV power to local load", "W", 0.1),


			"E_2_user_total":  		(1046, 2, rt.INPUT, dt.UINT32, float, "Energy to user total", "kWh", 0.1),
			"E_2_grid_total":  		(1050, 2, rt.INPUT, dt.UINT32, float, "Energy to grid total", "kWh", 0.1),

			"Bat_E_discharge":  	(1054, 2, rt.INPUT, dt.UINT32, float, "Total discharge energy", "kWh", 0.1),
			"Bat_E_charge":  		(1058, 2, rt.INPUT, dt.UINT32, float, "Total charge energy", "kWh", 0.1),

			"E_2_local_total":  	(1062, 2, rt.INPUT, dt.UINT32, float, "Energy to Local load total", "kWh", 0.1),


			"EPS1_U":  				(1068, 1, rt.INPUT, dt.UINT16, float, "EPS R Voltage", "V", 0.1),
			"EPS1_I":  				(1069, 1, rt.INPUT, dt.UINT16, float, "EPS R Current", "A", 0.1),
			"EPS1_P":  				(1070, 2, rt.INPUT, dt.UINT32, float, "EPS R Power", "W", 0.1),

			"EPS2_U":  				(1072, 1, rt.INPUT, dt.UINT16, float, "EPS S Voltage", "V", 0.1),
			"EPS2_I":  				(1073, 1, rt.INPUT, dt.UINT16, float, "EPS S Current", "A", 0.1),
			"EPS2_P":  				(1074, 2, rt.INPUT, dt.UINT32, float, "EPS S Power", "W", 0.1),

			"EPS3_U":  				(1076, 1, rt.INPUT, dt.UINT16, float, "EPS T Voltage", "V", 0.1),
			"EPS3_I":  				(1077, 1, rt.INPUT, dt.UINT16, float, "EPS T Current", "A", 0.1),
			"EPS3_P":  				(1078, 2, rt.INPUT, dt.UINT32, float, "EPS T Power", "W", 0.1),

			"EPS_load":  			(1080, 1, rt.INPUT, dt.UINT16, float, "EPS Load", "%", 0.1),


			#==========================================================================================================================

			"On_Off": 			(  0, 1, rt.HOLDING, dt.UINT16, int, "Remote On/Off", ["Off","On"], 1),
			"SaftyFuncEn": 			(  1, 1, rt.HOLDING, dt.RAW, self._saftyfunc, "Safty Functions", "", 1),
			"Active_P_Rate": 		(  3, 1, rt.HOLDING, dt.UINT16, int, "Inverter max output active power", "%", 1),
			"Pmax": 				(  6, 2, rt.HOLDING, dt.UINT32, int, "Nominal power", "VA", 1),

			"FW-Build": 			(  9, 6, rt.HOLDING, dt.STRING, str, "Firmware Build No", "", 1),
			"SerialNo": 			( 23, 5, rt.HOLDING, dt.STRING, str, "Serial Number", "", 1),

#			"Manufacturer_Info": 	( 34, 8, rt.HOLDING, dt.STRING, str, "Manufacturer Info", "", 1),
#			"BaudRate": 			( 22, 1, rt.HOLDING, dt.UINT16, int, "BaudRate", ["9600","38400"], 1),

			#----
			"Start_Delay": 			( 18, 1, rt.HOLDING, dt.UINT16, int, "Start Delay", "s", 1),

			"Restart_Delay": 		( 19, 1, rt.HOLDING, dt.UINT16, int, "Restart Delay Time after fault back", "s", 1),
			"Restart_Slope": 		( 20, 1, rt.HOLDING, dt.UINT16, float, "Restart Power start slope", "%", 0.1),

			"Lim_Vac_low1": 		( 52, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage low1 limit", "V", 0.1),
			"Lim_Vac_high1": 		( 53, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage high1 limit", "V", 0.1),

			"Lim_Fac_low1": 		( 54, 1, rt.HOLDING, dt.UINT16, int, "Grid frequency low1 limit", "Hz", 0.01),
			"Lim_Fac_high1": 		( 55, 1, rt.HOLDING, dt.UINT16, int, "Grid frequency high1 limit", "Hz", 0.01),

			"Lim_Vac_high2": 		( 57, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage high2 limit", "V", 0.1),
			
			"Lim_Vac_low1_time": 	( 68, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage low1 limit time", "ms", 20),
			"Lim_Vac_high1_time": 	( 69, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage high1 limit time", "ms", 20),

			"Lim_Fac_low1_time": 	( 72, 1, rt.HOLDING, dt.UINT16, int, "Grid frequency low1 limit time", "ms", 20),
			"Lim_Fac_high1_time": 	( 73, 1, rt.HOLDING, dt.UINT16, int, "Grid frequency high1 limit time", "ms", 20),

			"Lim_U10min": 			( 80, 1, rt.HOLDING, dt.UINT16, float, "Grid voltage protection 10min", "V", 0.1),

			"Lim_Vac_low2": 		( 56, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage low2 limit", "V", 0.1),
			"Lim_Vac_low2_time": 	( 70, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage low2 limit time", "ms", 20),

			"Lim_Vac_high2_time": 	( 71, 1, rt.HOLDING, dt.UINT16, int, "Grid voltage high2 limit time", "ms", 20),

			"Lim_connect_Vac_low": 	( 64, 1, rt.HOLDING, dt.UINT16, float, "Grid voltage connect low", "V", 0.1),
			"Lim_connect_Vac_high": ( 65, 1, rt.HOLDING, dt.UINT16, float, "Grid voltage connect high", "V", 0.1),

			"Lim_connect_Fac_low": 	( 66, 1, rt.HOLDING, dt.UINT16, float, "Grid frequency connect low", "Hz", 0.01),
			"Lim_connect_Fac_high": ( 67, 1, rt.HOLDING, dt.UINT16, float, "Grid frequency connect high", "Hz", 0.01),

			"Lim_LFSM-O_Start": 	( 91, 1, rt.HOLDING, dt.UINT16, float, "LFSM-O start", "Hz", 0.01),
			"Lim_LFSM-O_Rate": 		( 92, 1, rt.HOLDING, dt.UINT16, int, "LFSM-O rate", "% Pref/Hz", 1),

			"Qlockinpower": 		( 97, 1, rt.HOLDING, dt.UINT16, int, "Q(v) lock in active power", "%", 0.1),
			"QlockOutpower": 		( 98, 1, rt.HOLDING, dt.UINT16, int, "Q(v) lock out active power", "%", 0.1),

			"QlockInGridV": 		( 99, 1, rt.HOLDING, dt.UINT16, float, "Q(v) Lock in grid voltage",  "V", 0.1),
			"QlockOutGridV": 		(100, 1, rt.HOLDING, dt.UINT16, float, "Q(v) Lock out grid voltage", "V", 0.1),


			"QVRPDelayTime": 		(107, 1, rt.HOLDING, dt.UINT16, int, "Q(v) Reactive Power delaytime", "s", 1),

			"QPrzMax": 				(109, 1, rt.HOLDING, dt.UINT16, int, "Q(v) Qmax for curve", "%", 0.1),

			"PFModel": 				( 89, 1, rt.HOLDING, dt.UINT16, decode_pf, "PF Model", "", 1),
			"Power factor": 		(  2, 1, rt.HOLDING, dt.UINT16, int, "Inverter output power factor", "", 1),


			# out of scope?!
#			"Q": 					(137, 2, rt.HOLDING, dt.UINT32, int, "Reactive Power", "var", 0.1),


			#----
			"Sys-Date": 			( 45, 3, rt.HOLDING, dt.RAW, self._gwdate, "System Date", "", 1),
			"Sys-Time": 			( 48, 3, rt.HOLDING, dt.RAW, self._gwtime, "System Time", "", 1),

#			"ModbusVersion": 		( 73, 1, rt.HOLDING, dt.UINT16, str, "Modbus Version", "", 1),
			"ModbusVersion": 		( 88, 1, rt.HOLDING, dt.UINT16, str, "Modbus Version", "", 1),

#			"PFLineP1_LP": 			( 110, 1, rt.HOLDING, dt.UINT16, int, "PF limit line point 1 load percent", "%", 1),
#			"ExportLimit": 			( 122, 1, rt.HOLDING, dt.UINT16, int, "ExportLimit", "", 1),

			"BAT_CC":  				(1000, 1, rt.HOLDING, dt.UINT16, float, "Battery charge current", "A", 1),
			"BAT_LV":  				(1002, 1, rt.HOLDING, dt.UINT16, float, "Battery LV voltage", "V", 0.1),
			"BAT_StopDis":  		(1006, 1, rt.HOLDING, dt.UINT16, float, "Battery stop Discharge voltage", "V", 0.1),
			"BAT_CV":  				(1007, 1, rt.HOLDING, dt.UINT16, float, "Battery CV voltage", "V", 0.1),

			"GridFirst_StopSOC3":  	(1039, 1, rt.HOLDING, dt.UINT16, int, "Grid First: Stop Discharge SOC2", "%", 1),		# ok, getestet, ändern sich
			"GridFirst_StopSOC2":  	(1040, 1, rt.HOLDING, dt.UINT16, int, "Grid First: Stop Discharge SOC2", "%", 1),		# ok, getestet, ändern sich
			"BattFirst_StopSOC2":  	(1041, 1, rt.HOLDING, dt.UINT16, int, "Bat First: Stop Charge SOC when", "%", 1),		# ok, getestet, ändern sich
			"BattFirst_StopSOC3":  	(1042, 1, rt.HOLDING, dt.UINT16, int, "Bat First: Stop Charge SOC when", "%", 1),		# ok, getestet, ändern sich
			
			"Priority":  			(1044, 1, rt.HOLDING, dt.UINT16, int, "Priority", ["Load", "Bat","Grid"], 1),	#ok, read only
			"BattFirst_PowerRate":  (1045, 1, rt.HOLDING, dt.UINT16, int, "BatFirst PowerRate", "%", 1),
			
			#----
			"GridFirst_DischargeRate":  (1070, 1, rt.HOLDING, dt.UINT16, int, "Grid First: Discharge Power rate", "%", 1),
			"GridFirst_StopSOC":  		(1071, 1, rt.HOLDING, dt.UINT16, int, "Grid First: Stop Discharge SOC when", "%", 1),	# ok, getestet, ändern sich

			"GridFirst_Time1":  		(1080, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Grid First: Timer1", "", 1),
			"GridFirst_Time2":  		(1083, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Grid First: Timer2", "", 1),
			"GridFirst_Time3":  		(1086, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Grid First: Timer3", "", 1),

			"BattFirst_StopSOC":  		(1091, 1, rt.HOLDING, dt.UINT16, int, "Bat First: Stop Charge SOC when", "%", 1),		# ok, getestet, ändern sich
			"Batt_AC_charge":  			(1092, 1, rt.HOLDING, dt.UINT16, bool, "Bat AC_charge", "", 1),


			"BattFirst_Time1":  		(1100, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Batt First: Timer1", "", 1),
			"BattFirst_Time2":  		(1103, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Batt First: Timer2", "", 1),
			"BattFirst_Time3":  		(1106, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Batt First: Timer3", "", 1),

			"LoadFirst_Time1":  		(1110, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Load First: Timer1", "", 1),
			"LoadFirst_Time2":  		(1113, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Load First: Timer2", "", 1),
			"LoadFirst_Time3":  		(1116, 3, rt.HOLDING, dt.RAW, self._gwtimer, "Load First: Timer3", "", 1),

		}


	# convert Time from Growatt hex to HH:MM
	def _gwtime2(self, data):
		h = int(data[0], base=16)
		m = int(data[1], base=16)
		return f"{h:02d}:{m:02d}"

	def _gwdate(self, data):
		y = data.decode_16bit_uint()
		m = data.decode_16bit_uint()
		d = data.decode_16bit_uint()
		return str(datetime.date(y,m,d))

	def _gwtime(self, data):
		h = data.decode_16bit_uint()
		m = data.decode_16bit_uint()
		s = data.decode_16bit_uint()
		return str(datetime.time(h,m,s))

	def _gwtimer(self, data):
		sh = data.decode_8bit_uint()
		sm = data.decode_8bit_uint()
		eh = data.decode_8bit_uint()
		em = data.decode_8bit_uint()
		s  = (data.decode_16bit_uint() == 1)

		return f"{sh:02d}:{sm:02d} - {eh:02d}:{em:02d} {s}"
		
	def _saftyfunc(self, data):
		d = data.decode_16bit_uint()
		d = f"{d:>016b}"

		funcs = ["SPI", "AutoTestStart", "LVFRT", "FreqDerating", "Softstart", "DRMS" "PowerVoltFunc", "HVFRT", "ROCOF", "RecoverFreqDeratingMode"]

		efuncs = {}

		for idx, x in enumerate(funcs):
			efuncs[x] = d[idx] == "1"

		return efuncs
#		return f"{d} - {type(d)}"
#		return f"{d:>016b}"


	def _clean_data(self, results):
		return results

