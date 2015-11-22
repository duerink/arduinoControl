#from matplotlib import pylab
#from pylab import *

import subprocess
from os import listdir
#from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from arduinoControl.models import *
from arduinoControl.tasks import sendCommand
from django.contrib.auth.decorators import login_required
import datetime
import time
from datetime import datetime, date, timedelta
from django.utils import timezone

#@login_required
def index(request):
	temp = str(Temperature.objects.order_by('date_created').last().temperature_celsius)
	targetTemp = CVTarget.objects.order_by('date_set').last().target_temp
	regels = ["Current temperature: " + temp, 'Target Temperature: ' + str(targetTemp)]

	temps = Temperature.objects.filter(date_created__gte = (datetime.today() - timedelta(1))).all()
	chart_temps = []

	for temp in temps:

		datum = temp.date_created.strftime("%Y%m%d%H%M")
		#datum = temp.date_created
		chart_temps.append([datum, 
			round(float(temp.temperature_celsius), 2),
			round(float(temp.thermostat_target), 2)]
		)
	
	return render_to_response("arduinoControl/index.html", {
		'templist': regels,
		'chart_temps': chart_temps[:],
	})

@login_required
def dashboard(request):
	temps = Temperature.objects.filter(date_created__gte = (datetime.today() - timedelta(2))).all()
	chart_temps = []

	for temp in temps:
		datum = temp.date_created.strftime("%Y%m%d%H%M")
		#datum = temp.date_created
		chart_temps.append([datum, 
			round(float(temp.temperature_celsius), 2),
			round(float(temp.thermostat_target), 2)]
		)

	return render_to_response("arduinoControl/dashboard.html", {
		'chart_temps': chart_temps[:],
	})

@login_required
def alarminfo(request):
	day 		= DayOfWeek.objects.filter(weekday = datetime.today().weekday()+1)	#+1 maandag begint bij 0
	timeOfDay 	= datetime.time(datetime.now())
	kindOfDay 	= DayRoster.objects.filter(roster=1, day_of_week= day).last()
	setTask		= ArduinoTask.objects.filter(task_name = 'checkAlarm')
	timeItem 	= TimeItem.objects.filter(kind_of_day= kindOfDay.kind_of_day, task_name = ArduinoTask.objects.get(task_name = 'checkAlarm')).order_by('action_time').all()
	alarmList = []
	for item in timeItem:
		alarmList.append(item.action_time)
	return render_to_response("arduinoControl/index.html", {'templist': alarmList})

@login_required
def alarmoff(request):
	subprocess.call(['killall', 'mpg123'])
	regels = ['Alarm is off', 'I repeat the alarm is off']
	sendCommand('S')
	TaskLog(task_name = ArduinoTask.objects.get(task_name = 'checkAlarm'), task_result = False, task_decimal = 0,task_message = "I'm awake!", set_by = request.user).save()
	return render_to_response("arduinoControl/index.html", {'templist': regels})

@login_required
def alarmon(request):
	mp3_files = [ f for f in listdir('.') if f[-4:] == '.mp3' ]
	index=0
	#sendCommand('P')
	if not (len(mp3_files) > 0):
		result = "No mp3 files found!"
	else:
		subprocess.Popen(['mpg123', mp3_files[index]])
		result = '-- Playing: ' + mp3_files[index] + ' ---'
	regels = [result, 'Lights on']
	sendCommand('P')
	TaskLog(task_name = ArduinoTask.objects.get(task_name = 'checkAlarm'), task_result = True, task_decimal = 0,task_message = "Get up!", set_by = request.user).save()
	return render_to_response("arduinoControl/index.html", {'templist': regels})
	

#def plotTest(request
