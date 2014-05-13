from django.conf.urls import patterns, include, url
from django.contrib import admin
from leaderboards import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/$', views.leaderboard_detail, name='leaderboard_detail'),
	url(r'^$', views.leaderboards, name='leaderboards'),
)
