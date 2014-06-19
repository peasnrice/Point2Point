from django.conf.urls import patterns, include, url
from django.contrib import admin
from howtoplay import views
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.how_to_play, name='how to play'),
)
