# Taken voor background worker
# 
# Targets: losse caller en listener (verbeteren)
# Views voor vertraging > scheduler
# Daemonize celery
# Logging to db
# Uitzoeken nut pyFimata, opening port kost elke keer tijd....

from __future__ import absolute_import
from celery import Celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from decimal import Decimal
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from arduinoControl.models import *
from mysites.shared import *
import time
import os
import serial
#import pyglet		#Music playing ability
from os import listdir
import subprocess
#import pyfirmata

from celery import shared_task

# pyFirmata data for Arduino
#portList = ['/dev/ttyACM0', ' /dev/ttyACM1']
#board = pyfirmata.Arduino(port)

# Iterator to avoid buffer overflow
#it = pyfirmata.util.Iterator(board)
#it.start()

# Define pins
#tempPin = board.get_pin('a:0:i')
#ledPin = 11

def isDecimal(d):
	try:
		Decimal(d)
		return True
	except ValueError:
		 return False

def sendCommand(c):
	portList = ['/dev/ttyACM0', '/dev/ttyACM1']
	#try serial port
	#for x in range(0, len(portList)):
	#	try:
	#		#port = portList[x]
	#		ser = serial.Serial(portList[x], 9600)
	#		ser.close()
	#		port = portList[x]
	#		time.sleep(1)
	#		break
	#	except (OSError, serial.SerialException):
	#		 pass
	port = '/dev/ttyACM0'
	buffer = ''
	try:
		ser = serial.Serial(port, 9600)
		ser.write(c.encode())
		time.sleep(0.1)

		#ser.close()
		if c=='T' or c==' R' :
			buffer=''
			buffer = (ser.read(5)).decode("utf-8")
		ser.close()
		return buffer
	except ValueError:
		return False

# Not yet used, if used gives bug of waiting for next command (prob due to re-opening serialport)
def receiveAnswer():		
	ser = serial.Serial(port, 9600)
	buffer=''
	buffer = (ser.read(5)).decode("utf-8")
	return buffer 

@shared_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def setTemp():
	c =	CVTarget.objects.order_by('date_set').last()
	cur_targetTemp 	= c.target_temp
	setby			= c.set_by
	dateSet			= c.date_set 
	result = 'Not changed'
	if (setby != 'User'):
		day 		= DayOfWeek.objects.filter(weekday = datetime.today().weekday()+1)
		timeOfDay 	= datetime.time(datetime.now())
		kindOfDay 	= DayRoster.objects.filter(roster=1, day_of_week= day).last()
		setTask 	= ArduinoTask.objects.filter(task_name= 'setTemp')
		lastItem 	= TimeItem.objects.filter(kind_of_day= kindOfDay.kind_of_day,  task_name = ArduinoTask.objects.get(task_name = 'setTemp'), action_time__lte = timeOfDay).order_by('action_time').last()
		if lastItem != None:		# If no entries are available for the day yet
			targetTemp = lastItem.target_value
			result = result + ': ' + str(kindOfDay) + ', ' + str(lastItem.action_time)
			if (cur_targetTemp != targetTemp):
				new_cv =CVTarget(set_by= 'System', date_set = timezone.now(), target_temp = targetTemp).save()
				TaskLog(task_name =ArduinoTask.objects.get(task_name = 'setTemp'), task_result = True, task_decimal = Decimal(targetTemp), task_message = targetTemp, set_by = 'System').save()
				result = ('Target temp: ' + str(targetTemp))
	return result

@shared_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def getTemp():
	tempList = []
	while len(tempList) < 3:	# Get best average of 2 in list
		data = sendCommand('T') # And receive
		if (isDecimal(data)):
			tempList.append(Decimal(data))
	tempList.sort()
	if (tempList[1] - tempList[0]) < (tempList[2] - tempList[1]):
		data = Decimal((tempList[0] + tempList[1]) / 2)
	else:
		data = Decimal((tempList[1] + tempList[2]) / 2)
	setTask  		= ArduinoTask.objects.filter(task_name = 'getTemp')
	targetTemp 		= CVTarget.objects.order_by('date_set').last().target_temp
	Temperature(temperature_celsius = Decimal(data), thermostat_target = targetTemp, output_value = data).save()
	#TaskLog(task_name = ArduinoTask.objects.get(task_name = 'getTemp'), task_result = True, task_decimal = Decimal(data), task_message = data, set_by = 'System').save()
	return data

@shared_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def checkThermostat():
	lastTemp 		= Temperature.objects.order_by('date_created').last().temperature_celsius
	targetTemp 		= CVTarget.objects.order_by('date_set').last().target_temp
	setTask 		= ArduinoTask.objects.filter(task_name = 'setTemp')
	currentState 	= TaskLog.objects.filter(task_name = ArduinoTask.objects.get(task_name = 'checkTherm')).order_by('date_set').last().task_result
	#Thermostat.objects.order_by('date_set').last().heater_status
	result = 'Not changed'
	task = ArduinoTask.objects.filter(task_name = 'checkTherm')
	if lastTemp -targetTemp <0:
		if currentState ==False:
			h = TaskLog(task_name = ArduinoTask.objects.get(task_name = 'checkTherm'), task_result = True, task_message = 'Fire it up!', task_decimal = Decimal(targetTemp), set_by = 'System')
			#Thermostat(heater_status=True)
			sendCommand('L')
			h.save()
			result = 'Heater on'
	else:
		if currentState == True:
			h = TaskLog(task_name = ArduinoTask.objects.get(task_name = 'checkTherm'), task_result = False, task_message = 'Cool down!', task_decimal = Decimal(targetTemp), set_by = 'System')
			sendCommand('O')
			h.save()
			result = 'Heater off'
	return result

# Model: Alarm (wake-up: power on 220v, play music)
@shared_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def checkAlarm():
	result 		= 'Not changed'
	day 		= DayOfWeek.objects.filter(weekday = datetime.today().weekday()+1)	#+1 egint bij 0
	timeOfDay 	= datetime.time(datetime.now())
	kindOfDay 	= DayRoster.objects.filter(roster=1, day_of_week= day).last()
	setTask		= ArduinoTask.objects.filter(task_name = 'checkAlarm')
	lastItem 	= TimeItem.objects.filter(kind_of_day= kindOfDay.kind_of_day, task_name = ArduinoTask.objects.get(task_name = 'checkAlarm'), action_time__lte = timeOfDay).order_by('action_time').last()
	snoozeAlert = lastitem.target_value
	soundAlarm = False
	if lastItem != None:		# If no entries are available for the day yet
		lastAlarm 	= TaskLog.objects.filter(task_name = ArduinoTask.objects.get(task_name = 'checkAlarm')).order_by('date_set').last()
		#	lastAlarm = Alarm.objects.order_by('date_set').last()
		if datetime.date(lastAlarm.date_set) != datetime.date(datetime.now()):
			soundAlarm = True
			result = (str(datetime.date(lastAlarm.date_set)) + ' < ' + str(datetime.date(datetime.now())))
		elif (datetime.time(lastAlarm.date_set+ timedelta(hours=1)) < lastItem.action_time):
			soundAlarm = True
			result = (str(datetime.time(lastAlarm.date_set+ timedelta(hours=1))) + ' < ' + str(lastItem.action_time))
		else:
			soundAlarm = False
			result = (str(datetime.time(lastAlarm.date_set+ timedelta(hours=1))) + ' => ' + str(lastItem.action_time))
		if soundAlarm==True:
			#play music
			mp3_files = [ f for f in listdir('.') if f[-4:] == '.mp3' ]
			index=0
			sendCommand('P')
			if not (len(mp3_files) > 0):
				result = "No mp3 files found!"
			else:
				subprocess.Popen(['mpg123', mp3_files[index]])
				result = result + '-- Playing: ' + mp3_files[index] + ' ---'
			TaskLog(task_name = ArduinoTask.objects.get(task_name = 'checkAlarm'), task_result = True, task_decimal = 0,task_message = 'Wake up:' + mp3_files[index] + ' ---', set_by = 'System').save()
			if snoozeAlert == 99:
				lastItem.delete()
			#new_alarm = TaskLog(date_set = timezone.now(), alarm_status = True).save()
	else:
		result = str(kindOfDay) + ', No Alarm yet!'
	return result

