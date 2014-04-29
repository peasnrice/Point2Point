from django.conf.urls import patterns, include, url
from django.contrib import admin
from leaderboards import views
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.leaderboards, name='leaderboards'),
)
