from django.conf.urls import patterns, include, url
from contact import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.contact, name='contact'),
)
