from django.conf.urls import url

from . import views

urlpatterns =[
	url(r'^$', 'arduinoControl.views.index', name='index'),
#	url(r'^login/$', 'django.contrib.auth.views.login',{'template_name': 'admin/login.html'}),
	url(r'^temperature$', 'arduinoControl.views.index', name='index'),
	url(r'^dashboard$', 'arduinoControl.views.dashboard', name='dashboard'),
	url(r'^alarminfo$', 'arduinoControl.views.alarminfo', name='alarminfo'),
	url(r'^alarmoff$', 'arduinoControl.views.alarmoff', name='alarmoff'),
	url(r'^alarmon$', 'arduinoControl.views.alarmon', name='alarmoff'),
]
