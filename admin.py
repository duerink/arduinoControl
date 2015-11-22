from django.contrib import admin
#from .models import Temperature
#from .models import CV_Target
#from .models import Thermostat
from .models import *

class TemperatureAdmin(admin.ModelAdmin):
	list_display = ('date_created', 'temperature_celsius', 'thermostat_target')

#class ThermostatAdmin(admin.ModelAdmin):
#	list_display = ('date_set', 'heater_status')

class CVTargetAdmin(admin.ModelAdmin):
	list_display = ('date_set', 'set_by', 'target_temp')

class TimeItemsInLine(admin.StackedInline):
	model = TimeItem
	extra = 4
	ordering = ['action_time']

class KindOfDayAdmin(admin.ModelAdmin):
	inlines = [TimeItemsInLine]

class DayOfWeekAdmin(admin.ModelAdmin):
	ordering = ['weekday']

class DayRosterAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,			{'fields': ['roster']}),
		('Roster Info',	{'fields': ['day_of_week', 'kind_of_day']}),
	]
	ordering = ['roster', 'day_of_week']

class ArduinoTaskAdmin(admin.ModelAdmin):
	list_display= ('task_name', 'task_description')

class TaskLogAdmin(admin.ModelAdmin):
	list_display = ('date_set', 'task_name', 'task_result', 'task_decimal', 'task_message')
	list_filter = ('task_name',)

#class AlarmAdmin(admin.ModelAdmin):
#	list_display = ('date_set', 'alarm_status', 'alarm_result')
	
admin.site.register(Temperature, TemperatureAdmin)
admin.site.register(CVTarget, CVTargetAdmin)
#admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(DayOfWeek, DayOfWeekAdmin)
admin.site.register(KindOfDay, KindOfDayAdmin)
admin.site.register(DayRoster, DayRosterAdmin)
admin.site.register(ArduinoTask, ArduinoTaskAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
#admin.site.register(Alarm, AlarmAdmin)
#admin.site.register(TimeItem)

