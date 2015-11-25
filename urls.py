from django.conf.urls import url

from arduinoControl.views import MyView
from . import views

urlpatterns =[
	url(r'^$', 'arduinoControl.views.index', name='index'),
#	url(r'^login/$', 'django.contrib.auth.views.login',{'template_name': 'admin/login.html'}),
	 url(r'^about$', MyView.as_view()),
	url(r'^graphs$', 'arduinoControl.views.graphs', name='graphs'),
	url(r'^dashboard$', 'arduinoControl.views.dashboard', name='dashboard'),
	url(r'^alarmoff$', 'arduinoControl.views.alarmoff', name='alarmoff'),
	url(r'^alarmsnooze$', 'arduinoControl.views.alarmsnooze', name='alarmsnooze'),
	url(r'^alarmon$', 'arduinoControl.views.alarmon', name='alarmoff'),
]
