import time
import serial
import gc
import os
import pyvisa
import configparser
from pyvisa.constants import StopBits, Parity
import Gpib
import config.config_utils as cutil

#### Inizialization
# setting path to *.ini file
path_current_directory = os.path.dirname(__file__)
path_config_file = os.path.join(path_current_directory, 'config','lakeshore336_config.ini')

# configuration data
interface, timeout, loop, board_address, gpib_address, serial_address, baudrate, databits, parity, stopbits, write_termination, read_termination = cutil.read_conf_util(path_config_file)

#### Basic interaction functions
def connection():
	global status_flag
	global device
	
	if interface == 'gpib':
		try:
			device = Gpib.Gpib(board_address, gpib_address)
			try:
				# test should be here
				status_flag = 1;
				device_query('*IDN?')
			except pyvisa.VisaIOError:
				status_flag = 0;	
		except pyvisa.VisaIOError:
			print("No connection")
			device.close()
			status_flag = 0

	elif interface == 'rs232':
		try:
			rm = pyvisa.ResourceManager()
			device = rm.open_resource(serial_address,
					read_termination=read_termination, write_termination=write_termination, baud_rate = baudrate,
					data_bits = databits, parity=Parity.one, stop_bits=stopbits)
			device.timeout = timeout; # in ms
			try:
				# test should be here
				status_flag = 1;
				device_query('*IDN?')
			except:
				pass
		except pyvisa.VisaIOError:
			print("No connection")
			device.close()
			status_flag = 0
def close_connection():
	status_flag = 0;
	#device.close()
	gc.collect()
def device_write(command):
	if status_flag==1:
		command = str(command)
		device.write(command)
	else:
		print("No Connection")
def device_query(command):
	if status_flag == 1:
		if interface == 'gpib':
			device.write(command)
			time.sleep(0.05)
			answer = device.read()
		elif interface == 'rs232':
			answer = device.query(command)
		return answer
	else:
		print("No Connection")

#### Device specific functions
def tc_read_temp(channel):
	if channel=='A':
		try:
			answer = float(device_query('KRDG? A'))
		except TypeError:
			answer = 'No Connection';
		return answer
	elif channel=='B':
		try:
			answer = float(device_query('KRDG? B'))
		except TypeError:
			answer = 'No Connection';
		return answer
	elif channel=='C':
		try:
			answer = float(device_query('KRDG? C'))
		except TypeError:
			answer = 'No Connection';
		return answer
	elif channel=='D':
		try:
			answer = float(device_query('KRDG? D'))
		except TypeError:
			answer = 'No Connection';
		return answer
	else:
		print("Invalid Argument")	
def tc_set_temp(*temp):

	if len(temp)==1:
		temp = float(temp[0]);
		if temp < 330 and temp > 0.5:
			device.write('SETP '+ str(loop) + ', ' + str(temp))
		else:
			print("Invalid Argument")
	elif len(temp)==0:
		try:
			answer = float(device_query('SETP? '+ str(loop)))
		except TypeError:
			answer = 'No Connection';
		return answer	
	else:
		print("Invalid Argument")
def tc_heater_range(*heater):

	if len(heater)==1:
		heater = heater[0];
		if loop == 1 or loop == 2:
			if heater == '50W':
				device_write('RANGE ' + str(loop) + ', ' + str(3))
			elif heater == '5W':
				device_write('RANGE ' + str(loop) + ', ' + str(2))
			elif heater == '0.5W':
				device_write('RANGE ' + str(loop) + ', ' + str(1))
			elif heater == 'Off':
				device_write('RANGE ' + str(loop) + ', ' + str(0))
		elif loop == 3 or loop == 4:
			if heater == 'On':
				device_write('RANGE ' + str(loop) + ', ' + str(1))
			elif heater == 'Off':
				device_write('RANGE ' + str(loop) + ', ' + str(0))
	elif len(heater)==0:
		try:
			answer = int(device_query('RANGE?'))
		except TypeError:
			answer = 'No Connection';
		if answer == 3:
			answer = '50 W'
		if answer == 2:
			answer = '5 W'
		if answer == 1:
			answer = '0.5 W'
		if answer == 0:
			answer = 'Off'
		return answer
	else:
		print("Invalid Argument")								
def tc_heater():
	answer1 = tc_heater_range()
	answer = float(device_query('HTR?'))
	full_answer = [answer, answer1]
	return full_answer
