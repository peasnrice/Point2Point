from django.conf.urls import patterns, include, url
from django.contrib import admin
from home import views
from quests import web_views
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^quests/(?P<quest_type_id>\d+)/(?P<short_name>[-\w\d]+)/$', web_views.quest_list_type, name='quest_type'),
)
