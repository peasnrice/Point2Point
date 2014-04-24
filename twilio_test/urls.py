from django.conf.urls import patterns, url
from twilio_test import views

urlpatterns = patterns('',
    url(r'^verify_sms/$', views.verify_sms, name='verify_sms'),
)