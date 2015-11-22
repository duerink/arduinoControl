# Alles rond de thermostaat
# 
# Targets: temperatuur > DecimalField, mschrijvingen bij velden

from django.db 		import models
from datetime 		import datetime
from django.utils 	import timezone
from decimal 		import Decimal

class ArduinoTask(models.Model):
	task_name		= models.CharField(max_length=10)
	task_description	= models.CharField(max_length=200)
	def __str__(self):
		return str(self.task_name)

class Temperature(models.Model):
	temperature_celsius = models.DecimalField(max_digits=4, decimal_places=2)
	thermostat_target	= models.DecimalField(max_digits=4, decimal_places=2)
	output_value 		= models.CharField(max_length=50, default='')
	date_created 		= models.DateTimeField(default=timezone.now)
	def __str__(self):
		return (str(self.temperature_celsius))

class CVTarget(models.Model):
	target_temp = models.DecimalField(max_digits=4,decimal_places=2,default=Decimal('0.00'))
	date_set 	= models.DateTimeField(default=timezone.now)
	set_by 		= models.CharField(max_length=10, default='User')
	def __str__(self):
		return str(self.target_temp)

#class Thermostat(models.Model):
#	heater_status 	= models.BooleanField(default=False)
#	date_set 		= models.DateTimeField(default=timezone.now)
#	def __str__(self):
#		return str(self.heater_status)

class TimeItem(models.Model):
	kind_of_day = models.ForeignKey('KindOfDay')
	action_time = models.TimeField()
	task_name	= models.ForeignKey('ArduinoTask')
	target_value	= models.DecimalField(max_digits=4, decimal_places=2)

class KindOfDay(models.Model):
	kind_of_day = models.CharField(max_length=20)
	def __str__(self):
		return str(self.kind_of_day)

class DayRoster(models.Model):
	roster 			= models.ForeignKey('Roster')
	day_of_week 	= models.ForeignKey('DayOfWeek')
	kind_of_day 		= models.ForeignKey('KindOfDay')
	def __str__(self):
		return (str(self.roster) + ', ' + str(self.day_of_week) + ', ' + str(self.kind_of_day))

class DayOfWeek(models.Model):
	MONDAY 		= 1
	TUESDAY 		= 2
	WEDNESDAY 	= 3
	THURSDAY 	= 4
	FRIDAY 		= 5
	SATERDAY 		= 6
	SUNDAY 		= 7
	DAYS_IN_WEEK = (
		(MONDAY, 'Monday'),
		(TUESDAY, 'Tuesday'),
		(WEDNESDAY, 'Wednesday'),
		(THURSDAY, 'Thursday'),
		(FRIDAY, 'Friday'),
		(SATERDAY, 'Saterday'),
		(SUNDAY, 'Sunday'),
	)
	weekday = models.IntegerField(choices=DAYS_IN_WEEK, default = MONDAY)			# maandag ... zondag
	def __str__(self):
		return str(self.weekday)
	class Meta:
		ordering = ['weekday']

class Roster(models.Model):
	roster = models.CharField(max_length=20, default = 'Default')		#PM Standaard, Vakantie, ....
	def __str__(self):
		return str(self.roster)

class TaskLog(models.Model):
	task_name		= models.ForeignKey('ArduinoTask')
	#task_status 		= models.BooleanField(default=False)
	task_result		= models.BooleanField(default=False)
	task_message	= models.CharField(max_length=20, blank=True)
	task_decimal	= models.DecimalField(max_digits=5,decimal_places=2, blank=True)
	date_set 		= models.DateTimeField(default=timezone.now)
	set_by			= models.CharField(max_length=10, default='User', blank=True)
	def __str__(self):
		return str(self.task_name)
#	class Meta:
#		ordering = ['date_set', 'task_name']

# Model: Alarm (wake-up: power on 220v, play music)
class Alarm(models.Model):
	alarm_status 	= models.BooleanField(default=False)
	date_set 		= models.DateTimeField(default=timezone.now)
	alarm_result 	= models.BooleanField(default=False)
	def __str__(self):
		return str(self.alarm_status)
